"""RAG engine: embedding, retrieval, generation.

- Vectors live in a persistent local ChromaDB.
- Embeddings come from sentence-transformers (BGE-small) — runs fast on Mac CPU
  and avoids a second Ollama model load.
- Generation goes through the Ollama Python client. Streaming is supported.
"""
from __future__ import annotations

from typing import Iterable, Generator
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings

import ollama

from .config import (
    EMBED_MODEL, LLM_MODEL, OLLAMA_HOST, VECTOR_DIR,
    GENERATION_TEMPERATURE, MAX_CONTEXT_CHUNKS,
)
from .document_processor import Chunk


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

class _SentenceTransformerEmbedder:
    """Tiny wrapper that lazy-loads the model on first use."""
    _model = None

    @classmethod
    def model(cls):
        if cls._model is None:
            from sentence_transformers import SentenceTransformer
            cls._model = SentenceTransformer(EMBED_MODEL)
        return cls._model

    @classmethod
    def encode(cls, texts: list[str]) -> list[list[float]]:
        m = cls.model()
        vecs = m.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vecs.tolist()


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------

@dataclass
class RetrievedChunk:
    text: str
    source: str
    doc_id: str
    chunk_id: str
    page: int | None
    section: str | None
    score: float


class VectorStore:
    """Persistent Chroma collection scoped to a workspace."""

    def __init__(self, workspace: str = "default"):
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DIR),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
        self.workspace = workspace
        self.collection = self.client.get_or_create_collection(
            name=f"ws_{workspace}",
            metadata={"hnsw:space": "cosine"},
        )

    # ---------- writes ----------
    def add_chunks(self, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0

        # Defensive: deduplicate within the batch first. A buggy parser can
        # emit colliding chunk_ids; we'd rather silently drop the duplicate
        # than have Chroma raise DuplicateIDError on the whole batch.
        seen_in_batch: set[str] = set()
        deduped: list[Chunk] = []
        for c in chunks:
            if c.chunk_id in seen_in_batch:
                continue
            seen_in_batch.add(c.chunk_id)
            deduped.append(c)
        chunks = deduped

        # Skip chunks already present (stable chunk_id)
        existing = set()
        try:
            res = self.collection.get(ids=[c.chunk_id for c in chunks])
            existing = set(res.get("ids", []) or [])
        except Exception:
            pass

        new_chunks = [c for c in chunks if c.chunk_id not in existing]
        if not new_chunks:
            return 0

        embeddings = _SentenceTransformerEmbedder.encode([c.text for c in new_chunks])
        self.collection.add(
            ids=[c.chunk_id for c in new_chunks],
            embeddings=embeddings,
            documents=[c.text for c in new_chunks],
            metadatas=[c.to_metadata() for c in new_chunks],
        )
        return len(new_chunks)

    def delete_doc(self, doc_id: str) -> None:
        self.collection.delete(where={"doc_id": doc_id})

    def list_documents(self) -> list[dict]:
        try:
            res = self.collection.get()
        except Exception:
            return []
        sources: dict[str, dict] = {}
        for meta in res.get("metadatas", []) or []:
            doc_id = meta.get("doc_id")
            if not doc_id:
                continue
            d = sources.setdefault(doc_id, {
                "doc_id": doc_id,
                "source": meta.get("source"),
                "chunks": 0,
            })
            d["chunks"] += 1
        return sorted(sources.values(), key=lambda d: d["source"] or "")

    # ---------- reads ----------
    def query(self, question: str, k: int = MAX_CONTEXT_CHUNKS,
              doc_ids: list[str] | None = None) -> list[RetrievedChunk]:
        emb = _SentenceTransformerEmbedder.encode([question])[0]
        where = {"doc_id": {"$in": doc_ids}} if doc_ids else None
        res = self.collection.query(
            query_embeddings=[emb], n_results=k, where=where,
        )
        out: list[RetrievedChunk] = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for i, doc, meta, dist in zip(ids, docs, metas, dists):
            out.append(RetrievedChunk(
                text=doc,
                source=meta.get("source", "unknown"),
                doc_id=meta.get("doc_id", ""),
                chunk_id=i,
                page=meta.get("page"),
                section=meta.get("section"),
                score=1 - float(dist),  # convert cosine distance → similarity
            ))
        return out

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection.name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=f"ws_{self.workspace}",
            metadata={"hnsw:space": "cosine"},
        )


# ---------------------------------------------------------------------------
# Generation (Ollama)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are Atelier, a precise research assistant working strictly from the documents the user has uploaded.

Rules you follow without exception:
1. Ground every factual claim in the provided context. If the context does not answer the question, say so plainly — do not invent.
2. Cite sources inline using the format [#N] where N is the source number shown in the context block. Multiple sources are cited like [#1][#3].
3. Prefer concise, structured answers. Use bullet points for enumerations and short paragraphs for explanations.
4. When the user asks for an opinion or analysis, be direct and specific — vague hedging is unhelpful.
5. If the user asks something the documents cannot answer, suggest 1–2 follow-up questions that the documents could answer.
"""


def _format_context(retrieved: list[RetrievedChunk]) -> str:
    blocks = []
    for i, r in enumerate(retrieved, start=1):
        loc = []
        if r.page:
            loc.append(f"p.{r.page}")
        if r.section:
            loc.append(r.section)
        loc_str = f" ({', '.join(loc)})" if loc else ""
        blocks.append(f"[#{i}] {r.source}{loc_str}\n{r.text}")
    return "\n\n---\n\n".join(blocks)


def _ollama_client():
    return ollama.Client(host=OLLAMA_HOST)


def generate_answer_stream(
    question: str,
    retrieved: list[RetrievedChunk],
    history: list[dict] | None = None,
) -> Generator[str, None, None]:
    """Stream tokens from Ollama. Yields text fragments."""
    context = _format_context(retrieved) if retrieved else "(no documents matched)"
    history = history or []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Include a short tail of conversation history (last 6 turns)
    for m in history[-6:]:
        messages.append(m)
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {question}",
    })

    client = _ollama_client()
    stream = client.chat(
        model=LLM_MODEL,
        messages=messages,
        stream=True,
        options={"temperature": GENERATION_TEMPERATURE},
    )
    for chunk in stream:
        token = chunk.get("message", {}).get("content", "")
        if token:
            yield token


def generate_oneshot(prompt: str, *, temperature: float = 0.3,
                     system: str | None = None) -> str:
    """Non-streaming generation for summaries / analyses."""
    client = _ollama_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    res = client.chat(
        model=LLM_MODEL, messages=messages,
        options={"temperature": temperature},
    )
    return res["message"]["content"].strip()


def health_check() -> tuple[bool, str]:
    """Verify Ollama is up and the model is pulled."""
    try:
        client = _ollama_client()
        models = client.list().get("models", [])
        names = [m.get("model") or m.get("name") for m in models]
        if not any(LLM_MODEL.split(":")[0] in (n or "") for n in names):
            return False, (
                f"Ollama is reachable, but model '{LLM_MODEL}' is not pulled. "
                f"Run: `ollama pull {LLM_MODEL}`"
            )
        return True, f"Connected • {LLM_MODEL}"
    except Exception as e:
        return False, f"Ollama unreachable at {OLLAMA_HOST} — start it with `ollama serve`. ({e})"