"""Advanced analysis features layered on top of the RAG engine.

- Document summary (multi-pass, map-reduce style)
- Recommended questions
- Key entities & themes
- Numeric trend extraction (for spreadsheet documents)
"""
from __future__ import annotations

import io
import json
import re
from collections import Counter
from dataclasses import dataclass

import pandas as pd

from .rag_engine import generate_oneshot, VectorStore
from .document_processor import Chunk
from .config import SUMMARY_TEMPERATURE, ANALYSIS_TEMPERATURE


# ---------------------------------------------------------------------------
# Summary (map-reduce so it works for long docs with an 8B model)
# ---------------------------------------------------------------------------

_PARTIAL_SUMMARY_SYS = (
    "You summarize a single section of a larger document. "
    "Capture only the concrete claims, facts, numbers, and named entities in the text. "
    "Output 4–8 dense bullet points. Do not editorialize."
)

_FINAL_SUMMARY_SYS = (
    "You write executive briefings. Given a set of section notes from one document, "
    "produce a clean briefing with the following sections:\n"
    "  • Overview — 2–3 sentences on what the document is and why it exists.\n"
    "  • Key Points — 5–8 bullets covering the most important content.\n"
    "  • Notable Numbers — concrete figures, dates, percentages (if any).\n"
    "  • Open Questions — things the document raises but does not answer.\n"
    "Be concise and specific. No filler."
)


def summarize_document(chunks: list[Chunk]) -> str:
    """Map-reduce summary that works on llama3:8b within typical context."""
    if not chunks:
        return "_No content to summarize._"

    # Group chunks into batches of ~3000 chars for the map step
    batches: list[str] = []
    buf, buf_len = [], 0
    for c in chunks:
        if buf_len + len(c.text) > 3000 and buf:
            batches.append("\n\n".join(buf))
            buf, buf_len = [], 0
        buf.append(c.text)
        buf_len += len(c.text)
    if buf:
        batches.append("\n\n".join(buf))

    # Cap to first ~8 batches — for very long books this is the head;
    # users can ask follow-ups for deeper sections.
    batches = batches[:8]

    partial_notes: list[str] = []
    for i, b in enumerate(batches, start=1):
        notes = generate_oneshot(
            f"Section {i}/{len(batches)}:\n\n{b}",
            temperature=SUMMARY_TEMPERATURE,
            system=_PARTIAL_SUMMARY_SYS,
        )
        partial_notes.append(notes)

    final = generate_oneshot(
        "Section notes:\n\n" + "\n\n".join(
            f"## Section {i}\n{n}" for i, n in enumerate(partial_notes, start=1)
        ),
        temperature=SUMMARY_TEMPERATURE,
        system=_FINAL_SUMMARY_SYS,
    )
    return final


# ---------------------------------------------------------------------------
# Recommended questions
# ---------------------------------------------------------------------------

_QUESTIONS_SYS = (
    "You generate sharp, specific questions a reader could ask about a document. "
    "Each question must be answerable from the document content provided. "
    "Mix factual lookups, comparative questions, and questions that surface implications. "
    "Output STRICTLY a JSON array of strings, no prose, no markdown, no code fence."
)


def recommend_questions(chunks: list[Chunk], n: int = 6) -> list[str]:
    if not chunks:
        return []
    # Use a sample (head + middle + tail) to give the model a representative view
    sample = _sample_chunks(chunks, max_chars=4000)
    raw = generate_oneshot(
        f"Generate {n} questions a reader might ask about this document:\n\n{sample}",
        temperature=ANALYSIS_TEMPERATURE,
        system=_QUESTIONS_SYS,
    )
    return _parse_json_list(raw)[:n]


# ---------------------------------------------------------------------------
# Key entities & themes
# ---------------------------------------------------------------------------

_ENTITIES_SYS = (
    "You extract structured information from a document excerpt. "
    "Output STRICTLY a JSON object with these keys:\n"
    '  - "people": array of named people\n'
    '  - "organizations": array of organizations\n'
    '  - "places": array of places\n'
    '  - "dates_or_periods": array of specific dates or time periods\n'
    '  - "themes": array of 4–7 short thematic phrases (2–4 words each)\n'
    "Each array contains unique strings only. No prose, no markdown, no code fence."
)


def extract_entities_and_themes(chunks: list[Chunk]) -> dict:
    if not chunks:
        return {"people": [], "organizations": [], "places": [],
                "dates_or_periods": [], "themes": []}
    sample = _sample_chunks(chunks, max_chars=5000)
    raw = generate_oneshot(
        f"Document excerpt:\n\n{sample}",
        temperature=ANALYSIS_TEMPERATURE,
        system=_ENTITIES_SYS,
    )
    obj = _parse_json_object(raw)
    # Defensive defaults
    for key in ("people", "organizations", "places", "dates_or_periods", "themes"):
        obj.setdefault(key, [])
        if not isinstance(obj[key], list):
            obj[key] = []
        # Dedupe + cap
        seen, clean = set(), []
        for v in obj[key]:
            if isinstance(v, str) and v.strip() and v.strip().lower() not in seen:
                seen.add(v.strip().lower())
                clean.append(v.strip())
        obj[key] = clean[:25]
    return obj


# ---------------------------------------------------------------------------
# Cross-document Q&A — generate questions that span multiple uploaded docs
# ---------------------------------------------------------------------------

def cross_document_questions(store: VectorStore, n: int = 5) -> list[str]:
    docs = store.list_documents()
    if len(docs) < 2:
        return []
    names = [d["source"] for d in docs[:6]]
    raw = generate_oneshot(
        "I have these documents in my workspace:\n- " + "\n- ".join(names) +
        f"\n\nGenerate {n} questions whose answers would require comparing or combining "
        "information across two or more of these documents. Output STRICTLY a JSON array of strings.",
        temperature=ANALYSIS_TEMPERATURE,
        system="You are a research assistant. Output JSON only.",
    )
    return _parse_json_list(raw)[:n]


# ---------------------------------------------------------------------------
# Trend analysis — for spreadsheet-style documents
# ---------------------------------------------------------------------------

@dataclass
class TrendSeries:
    label: str
    x: list           # categories or time labels
    y: list           # numeric values
    summary: str      # one-line interpretation


def detect_trends(file_bytes: bytes, filename: str) -> list[TrendSeries]:
    """Lightweight numeric trend detection for xlsx/csv files.

    For each numeric column, returns a TrendSeries with the column values
    plotted against the first non-numeric column (typically a date or label).
    """
    ext = filename.split(".")[-1].lower()
    sheets: dict[str, pd.DataFrame] = {}
    try:
        if ext in ("xlsx", "xls"):
            xls = pd.ExcelFile(io.BytesIO(file_bytes))
            for s in xls.sheet_names:
                sheets[s] = xls.parse(s)
        elif ext == "csv":
            sheets["csv"] = pd.read_csv(io.BytesIO(file_bytes))
        else:
            return []
    except Exception:
        return []

    out: list[TrendSeries] = []
    for sheet_name, df in sheets.items():
        if df.empty:
            continue
        df = df.dropna(how="all").dropna(how="all", axis=1)
        if df.empty:
            continue

        # Find an x-axis: first non-numeric column, or the index
        x_col = None
        for c in df.columns:
            if not pd.api.types.is_numeric_dtype(df[c]):
                x_col = c
                break
        x_values = df[x_col].astype(str).tolist() if x_col else list(range(1, len(df) + 1))

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        for col in numeric_cols[:6]:  # cap visualizations
            series = df[col].dropna()
            if len(series) < 2:
                continue
            y_values = series.tolist()
            x_aligned = [x_values[i] for i in series.index if i < len(x_values)]
            summary = _trend_one_liner(y_values)
            label = f"{sheet_name} • {col}" if len(sheets) > 1 else str(col)
            out.append(TrendSeries(label=label, x=x_aligned, y=y_values, summary=summary))
    return out


def _trend_one_liner(values: list[float]) -> str:
    if len(values) < 2:
        return "insufficient data"
    start, end = float(values[0]), float(values[-1])
    peak = max(values)
    trough = min(values)
    if start == 0:
        change = "n/a"
    else:
        change = f"{((end - start) / abs(start)) * 100:+.1f}%"
    return (
        f"Start {start:,.2f} → end {end:,.2f} ({change}). "
        f"Peak {peak:,.2f}, trough {trough:,.2f}."
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sample_chunks(chunks: list[Chunk], max_chars: int = 4000) -> str:
    """Pick representative chunks: head + middle + tail."""
    if not chunks:
        return ""
    n = len(chunks)
    picks: list[Chunk] = []
    if n <= 5:
        picks = chunks
    else:
        picks = [
            chunks[0], chunks[1],
            chunks[n // 2 - 1], chunks[n // 2], chunks[n // 2 + 1],
            chunks[-2], chunks[-1],
        ]
    out, total = [], 0
    for c in picks:
        if total + len(c.text) > max_chars:
            break
        out.append(c.text)
        total += len(c.text)
    return "\n\n".join(out)


def _parse_json_list(raw: str) -> list[str]:
    """Robustly extract a JSON array of strings from model output."""
    s = raw.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.MULTILINE)
    # Find first [ ... ]
    m = re.search(r"\[.*\]", s, flags=re.DOTALL)
    if m:
        s = m.group(0)
    try:
        arr = json.loads(s)
        return [str(x).strip() for x in arr if str(x).strip()]
    except Exception:
        # Fallback — split by lines that look like questions
        return [
            line.lstrip("-• 0123456789.)\t ").strip(' "')
            for line in raw.splitlines()
            if "?" in line
        ][:10]


def _parse_json_object(raw: str) -> dict:
    s = raw.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.MULTILINE)
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    if m:
        s = m.group(0)
    try:
        return json.loads(s)
    except Exception:
        return {}
