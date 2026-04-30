"""DocuAgent AI — Secure AI Document Intelligence Platform.

Run with:
    streamlit run app.py
"""
from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

from core.config import APP_NAME, APP_TAGLINE, SUPPORTED_EXTENSIONS, LLM_MODEL
from core.document_processor import process_upload, document_summary_card, parse_url
from core.rag_engine import VectorStore, generate_answer_stream, health_check
from core.analyzer import (
    summarize_document, recommend_questions, extract_entities_and_themes,
    cross_document_questions, detect_trends,
)
from ui import styles


# ---------------------------------------------------------------------------
# Page config + global styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title=f"{APP_NAME} AI · {APP_TAGLINE}",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)
styles.inject()


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def _init_state():
    ss = st.session_state
    ss.setdefault("workspace", "default")
    ss.setdefault("messages", [])  # [{role, content, sources?: list}]
    ss.setdefault("doc_index", {})  # doc_id -> {source, chunks, summary, entities, questions, trends}
    ss.setdefault("active_doc_ids", [])  # filter retrieval to these docs (empty = all)
    ss.setdefault("pending_question", None)
    ss.setdefault("uploaded_blobs", {})  # filename -> bytes (kept for trend recompute)


_init_state()


@st.cache_resource(show_spinner=False)
def get_store(workspace: str) -> VectorStore:
    return VectorStore(workspace=workspace)


store = get_store(st.session_state.workspace)


def _seed_doc_index_from_store():
    """On a fresh session (e.g. after Streamlit restart), repopulate the
    sidebar's source list from the persistent vector store so the user
    doesn't appear to have lost their indexed documents.
    """
    if st.session_state.doc_index:
        return
    for d in store.list_documents():
        doc_id = d.get("doc_id")
        if not doc_id:
            continue
        source = d.get("source") or "(untitled)"
        ext = Path(source).suffix.lower().lstrip(".") or "doc"
        st.session_state.doc_index[doc_id] = {
            "doc_id": doc_id,
            "source": source,
            "ext": ext,
            "chunks": d.get("chunks", 0),
            "pages": None,
            "sections": None,
            "characters": None,
            "approx_words": 0,
            "summary": None,
            "entities": None,
            "questions": None,
            "trends": None,
        }


_seed_doc_index_from_store()


# ---------------------------------------------------------------------------
# Sidebar — workspace, sources, ingestion
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        f'<div class="brand">'
        f'<div class="brand-main">'
        f'<span class="brand-mark">{APP_NAME}<span class="brand-ai"> AI</span></span>'
        f'</div>'
        f'<div class="brand-sub">{APP_TAGLINE}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    ok, msg = health_check()
    styles.status_pill(ok, msg)
    styles.privacy_bar()

    styles.rule_heading("Data Sources")
    styles.sidebar_helper("Upload files or add a URL to build your private knowledge base.")

    uploads = st.file_uploader(
        "Drag & drop or click to upload",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True,
        label_visibility="visible",
    )

    url = st.text_input("Or paste a URL", placeholder="https://example.com/article",
                        label_visibility="visible")
    fetch = st.button("Add URL", use_container_width=True, disabled=not url.strip())

    # --- handle uploads ---
    if uploads:
        for up in uploads:
            data = up.getvalue()
            if up.name in [d["source"] for d in st.session_state.doc_index.values()]:
                continue
            with st.spinner(f"Parsing {up.name}…"):
                try:
                    chunks = process_upload(up.name, data)
                except Exception as e:
                    st.error(f"Could not parse {up.name}: {e}")
                    continue
                if not chunks:
                    st.warning(f"No text extracted from {up.name}.")
                    continue
                added = store.add_chunks(chunks)
                card = document_summary_card(chunks)
                st.session_state.doc_index[card["doc_id"]] = {
                    **card,
                    "ext": Path(up.name).suffix.lower().lstrip("."),
                    "summary": None, "entities": None,
                    "questions": None, "trends": None,
                }
                st.session_state.uploaded_blobs[up.name] = data
            st.toast(f"Indexed {up.name} • {added} chunks")
        st.rerun()

    if fetch and url.strip():
        with st.spinner(f"Fetching {url}…"):
            try:
                chunks = parse_url(url.strip())
                store.add_chunks(chunks)
                card = document_summary_card(chunks)
                st.session_state.doc_index[card["doc_id"]] = {
                    **card, "ext": "url",
                    "summary": None, "entities": None,
                    "questions": None, "trends": None,
                }
                st.toast(f"Indexed {url}")
                st.rerun()
            except Exception as e:
                st.error(f"Fetch failed: {e}")

    # --- source list ---
    if st.session_state.doc_index:
        doc_count = len(st.session_state.doc_index)
        styles.rule_heading(f"Indexed Sources ({doc_count})")
        # Re-read from store so the list survives reruns
        live_docs = {d["doc_id"]: d for d in store.list_documents()}

        for doc_id, info in list(st.session_state.doc_index.items()):
            if doc_id not in live_docs:
                # Fell out of the store somehow — drop from local index
                st.session_state.doc_index.pop(doc_id, None)
                continue

            label = info["source"]
            short = (label[:38] + "…") if len(label) > 40 else label
            ext = info.get("ext", "").upper() or "DOC"
            words = info.get("approx_words", 0)
            pages = info.get("pages")

            meta_parts = [ext]
            if pages:
                meta_parts.append(f"{pages}p")
            if words:
                meta_parts.append(f"~{words:,} words")
            meta = " · ".join(meta_parts)

            with st.container():
                st.markdown(
                    f'<div class="card"><div class="card-title">{short}</div>'
                    f'<div class="card-meta">{meta}</div></div>',
                    unsafe_allow_html=True,
                )
                cols = st.columns([1, 1])
                if cols[0].button("Filter", key=f"focus_{doc_id}", use_container_width=True):
                    st.session_state.active_doc_ids = [doc_id]
                    st.rerun()
                if cols[1].button("Delete", key=f"del_{doc_id}", use_container_width=True):
                    store.delete_doc(doc_id)
                    st.session_state.doc_index.pop(doc_id, None)
                    st.session_state.uploaded_blobs.pop(info["source"], None)
                    if doc_id in st.session_state.active_doc_ids:
                        st.session_state.active_doc_ids.remove(doc_id)
                    st.toast("Removed source.")
                    st.rerun()

        # Filter status
        if st.session_state.active_doc_ids:
            current = ", ".join(
                st.session_state.doc_index[d]["source"][:28]
                for d in st.session_state.active_doc_ids
                if d in st.session_state.doc_index
            )
            st.caption(f"🔎 Filtered: {current}")
            if st.button("Show All Sources", key="clear_focus", use_container_width=True):
                st.session_state.active_doc_ids = []
                st.rerun()


# ---------------------------------------------------------------------------
# Main — hero + tabs
# ---------------------------------------------------------------------------

styles.hero(
    APP_NAME,
    "Ask questions, extract insights, and analyze documents — 100% locally and securely. "
    "Unlike cloud AI tools, your data never leaves this machine.",
)

if not st.session_state.doc_index:
    styles.rule_heading("Get Started")
    st.markdown(
        '<div class="get-started-wrap">'
        '<p class="get-started-sub">'
        'Upload a PDF, Word doc, spreadsheet, presentation, EPUB, or paste a URL in the '
        'sidebar to build your private knowledge base. '
        'The first index takes a moment while the embedding model loads — subsequent uploads are fast.'
        '</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="card"><div class="card-title">What you can ask</div>'
        '<div class="card-meta" style="line-height:1.85; font-family: DM Sans, sans-serif; '
        'font-size: 0.875rem; color: var(--text-dim); letter-spacing: 0;">'
        '&ldquo;Summarize this 50-page contract in 5 bullet points.&rdquo;<br>'
        '&ldquo;What are the key risks and obligations in this agreement?&rdquo;<br>'
        '&ldquo;Compare financial trends across these uploaded reports.&rdquo;<br>'
        '&ldquo;Extract all deadlines, parties, and penalties from this document.&rdquo;<br>'
        '&ldquo;Find contradictions or inconsistencies across multiple documents.&rdquo;'
        "</div></div>",
        unsafe_allow_html=True,
    )
    st.stop()


tab_chat, tab_summary, tab_analysis, tab_trends, tab_workspace = st.tabs(
    ["  Chat  ", "  Summary  ", "  Analysis  ", "  Trends  ", "  Workspace  "]
)


# ---------------------------------------------------------------------------
# Tab — Conversation (chat)
# ---------------------------------------------------------------------------

with tab_chat:
    styles.grounded_note()

    # Suggested questions row (auto-generated, single-doc focused)
    if (st.session_state.active_doc_ids and not st.session_state.messages):
        focused_id = st.session_state.active_doc_ids[0]
        info = st.session_state.doc_index.get(focused_id, {})
        if info.get("questions") is None:
            with st.spinner("Generating starter questions…"):
                try:
                    # Re-pull this doc's chunks from the store for question gen
                    # (cheap because we already have them embedded)
                    res = store.collection.get(where={"doc_id": focused_id})
                    docs = res.get("documents") or []
                    metas = res.get("metadatas") or []
                    from core.document_processor import Chunk as _C
                    fake = [_C(text=d, source=m.get("source",""), doc_id=focused_id,
                               chunk_id=m.get("chunk_id","x"),
                               page=m.get("page"), section=m.get("section"))
                            for d, m in zip(docs, metas)]
                    info["questions"] = recommend_questions(fake, n=5)
                except Exception:
                    info["questions"] = []  # silent fallback — chat still works
                st.session_state.doc_index[focused_id] = info

        qs = info.get("questions") or []
        if qs:
            styles.rule_heading("Suggested Questions")
            cols = st.columns(min(len(qs), 3) or 1)
            for i, q in enumerate(qs):
                if cols[i % len(cols)].button(q, key=f"sugg_{i}", use_container_width=True):
                    st.session_state.pending_question = q

    # Cross-doc questions when multiple docs and no focus
    if (len(st.session_state.doc_index) >= 2
        and not st.session_state.active_doc_ids
        and not st.session_state.messages):
        cdq_key = "cdq"
        if cdq_key not in st.session_state:
            with st.spinner("Looking for connections across your documents…"):
                try:
                    st.session_state[cdq_key] = cross_document_questions(store, n=4)
                except Exception:
                    st.session_state[cdq_key] = []
        cdq = st.session_state[cdq_key]
        if cdq:
            styles.rule_heading("Cross-Document Insights")
            cols = st.columns(min(len(cdq), 2) or 1)
            for i, q in enumerate(cdq):
                if cols[i % len(cols)].button(q, key=f"cdq_{i}", use_container_width=True):
                    st.session_state.pending_question = q

    # Render conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(f'<div class="answer-body">{msg["content"]}</div>',
                        unsafe_allow_html=True)
            if msg.get("sources"):
                n = len(msg["sources"])
                chips = "".join(
                    f'<span class="src-chip">[{i+1}] {s["source"]}'
                    + (f" · p.{s['page']}" if s.get("page") else "")
                    + "</span>"
                    for i, s in enumerate(msg["sources"])
                )
                with st.expander(f"📎 Citations & Sources ({n})", expanded=False):
                    st.markdown(chips, unsafe_allow_html=True)
                    for i, s in enumerate(msg["sources"]):
                        st.markdown(
                            f"**[{i+1}] {s['source']}**"
                            + (f"  ·  p.{s['page']}" if s.get("page") else "")
                            + (f"  ·  {s['section']}" if s.get("section") else "")
                        )
                        st.caption(s["text"][:500] + ("…" if len(s["text"]) > 500 else ""))

    # Input
    user_msg = st.chat_input("Ask anything about your sources…")
    if st.session_state.pending_question:
        user_msg = st.session_state.pending_question
        st.session_state.pending_question = None

    if user_msg:
        st.session_state.messages.append({"role": "user", "content": user_msg})
        with st.chat_message("user"):
            st.markdown(f'<div class="answer-body">{user_msg}</div>',
                        unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("Searching your documents…"):
                try:
                    retrieved = store.query(
                        user_msg,
                        doc_ids=st.session_state.active_doc_ids or None,
                    )
                except Exception as e:
                    st.error(f"Retrieval failed: {e}")
                    retrieved = []
            placeholder = st.empty()
            history_for_llm = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
            buffer = ""
            try:
                for token in generate_answer_stream(
                    user_msg, retrieved, history=history_for_llm
                ):
                    buffer += token
                    placeholder.markdown(
                        f'<div class="answer-body">{buffer}▍</div>',
                        unsafe_allow_html=True,
                    )
                placeholder.markdown(
                    f'<div class="answer-body">{buffer}</div>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                err = (
                    "_Generation failed. Make sure Ollama is running "
                    f"(`ollama serve`) and the model is pulled. Details: {e}_"
                )
                placeholder.markdown(
                    f'<div class="answer-body">{err}</div>',
                    unsafe_allow_html=True,
                )
                buffer = err

            sources_payload = [
                {"source": r.source, "page": r.page, "section": r.section,
                 "text": r.text}
                for r in retrieved
            ]
            with st.expander(f"📎 Citations & Sources ({len(retrieved)})", expanded=False):
                for i, r in enumerate(retrieved, start=1):
                    head = f"**[{i}] {r.source}**"
                    if r.page: head += f"  ·  p.{r.page}"
                    if r.section: head += f"  ·  {r.section}"
                    confidence = int(r.score * 100)
                    head += f"  ·  confidence {confidence}%"
                    st.markdown(head)
                    st.caption(r.text[:500] + ("…" if len(r.text) > 500 else ""))

        st.session_state.messages.append({
            "role": "assistant", "content": buffer, "sources": sources_payload
        })

    if st.session_state.messages:
        styles.ornament()
        col_clear, col_pad = st.columns([1, 4])
        if col_clear.button("Clear Chat", key="clear_conversation"):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()


# ---------------------------------------------------------------------------
# Tab — Summary
# ---------------------------------------------------------------------------

with tab_summary:
    docs = list(st.session_state.doc_index.values())
    if not docs:
        st.info("Add a document to generate a summary.")
    else:
        chosen_label = st.selectbox(
            "Document",
            options=[d["source"] for d in docs],
            label_visibility="collapsed",
        )
        chosen = next(d for d in docs if d["source"] == chosen_label)
        doc_id = chosen["doc_id"]

        styles.rule_heading("Executive Briefing")
        if chosen.get("summary"):
            st.markdown(f'<div class="answer-body">{chosen["summary"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.info("No summary generated yet. Click below to create one.")

        if st.button("Generate Briefing", type="primary"):
            with st.spinner("Synthesizing document… this may take 30–60s on first run."):
                try:
                    res = store.collection.get(where={"doc_id": doc_id})
                    docs_text = res.get("documents") or []
                    metas = res.get("metadatas") or []
                    from core.document_processor import Chunk as _C
                    chunks = [_C(text=d, source=m.get("source",""), doc_id=doc_id,
                                 chunk_id=m.get("chunk_id","x"),
                                 page=m.get("page"), section=m.get("section"))
                              for d, m in zip(docs_text, metas)]
                    summary = summarize_document(chunks)
                    st.session_state.doc_index[doc_id]["summary"] = summary
                except Exception as e:
                    st.error(f"Could not generate briefing: {e}")
            st.rerun()


# ---------------------------------------------------------------------------
# Tab — Analysis (entities, themes)
# ---------------------------------------------------------------------------

with tab_analysis:
    docs = list(st.session_state.doc_index.values())
    if not docs:
        st.info("Add a document to run analysis.")
    else:
        chosen_label = st.selectbox(
            "Document", options=[d["source"] for d in docs],
            label_visibility="collapsed", key="analysis_doc",
        )
        chosen = next(d for d in docs if d["source"] == chosen_label)
        doc_id = chosen["doc_id"]
        ents = chosen.get("entities")

        if not ents:
            if st.button("Run Deep Analysis", type="primary"):
                with st.spinner("Extracting entities, themes, and key questions…"):
                    try:
                        res = store.collection.get(where={"doc_id": doc_id})
                        docs_text = res.get("documents") or []
                        metas = res.get("metadatas") or []
                        from core.document_processor import Chunk as _C
                        chunks = [_C(text=d, source=m.get("source",""), doc_id=doc_id,
                                     chunk_id=m.get("chunk_id","x"),
                                     page=m.get("page"), section=m.get("section"))
                                  for d, m in zip(docs_text, metas)]
                        ents = extract_entities_and_themes(chunks)
                        qs = recommend_questions(chunks, n=8)
                        st.session_state.doc_index[doc_id]["entities"] = ents
                        st.session_state.doc_index[doc_id]["questions"] = qs
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
                st.rerun()
        else:
            qs = chosen.get("questions") or []

            cols = st.columns(2)
            with cols[0]:
                styles.rule_heading("Key Themes")
                for t in ents.get("themes", []):
                    st.markdown(
                        f'<span class="src-chip" style="background:rgba(200,155,60,0.18);'
                        f'border-color:var(--accent-line);">{t}</span>',
                        unsafe_allow_html=True,
                    )

                styles.rule_heading("People")
                st.markdown(", ".join(ents.get("people", [])) or "_none identified_")

                styles.rule_heading("Organizations")
                st.markdown(", ".join(ents.get("organizations", [])) or "_none identified_")

            with cols[1]:
                styles.rule_heading("Places")
                st.markdown(", ".join(ents.get("places", [])) or "_none identified_")

                styles.rule_heading("Dates & Periods")
                st.markdown(", ".join(ents.get("dates_or_periods", [])) or "_none identified_")

                styles.rule_heading("Recommended Questions")
                for i, q in enumerate(qs):
                    if st.button(q, key=f"aq_{doc_id}_{i}", use_container_width=True):
                        st.session_state.pending_question = q
                        st.session_state.active_doc_ids = [doc_id]
                        st.toast("Question sent to Chat tab.")

            if st.button("Re-run Analysis"):
                st.session_state.doc_index[doc_id]["entities"] = None
                st.session_state.doc_index[doc_id]["questions"] = None
                st.rerun()


# ---------------------------------------------------------------------------
# Tab — Trends (numeric)
# ---------------------------------------------------------------------------

with tab_trends:
    # Only show docs we still have raw bytes for AND that are tabular
    tabular = []
    for fname, data in st.session_state.uploaded_blobs.items():
        if fname.lower().endswith((".xlsx", ".xls", ".csv")):
            tabular.append((fname, data))

    if not tabular:
        st.info(
            "Trends works on spreadsheets and CSVs. Upload a `.xlsx` or `.csv` file "
            "and DocuAgent AI will automatically chart every numeric series and surface insights."
        )
    else:
        labels = [f for f, _ in tabular]
        chosen = st.selectbox("Spreadsheet", options=labels, label_visibility="collapsed")
        data = dict(tabular)[chosen]

        if st.button("Detect Trends", type="primary"):
            with st.spinner("Profiling numeric columns and computing trends…"):
                series = detect_trends(data, chosen)
                st.session_state[f"trends_{chosen}"] = series

        series = st.session_state.get(f"trends_{chosen}", [])
        if not series:
            st.caption("Click the button above to scan numeric columns and generate charts.")
        else:
            for s in series:
                styles.rule_heading(s.label)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=s.x, y=s.y, mode="lines+markers",
                    line=dict(color="#c89b3c", width=2),
                    marker=dict(size=6, color="#c89b3c"),
                    fill="tozeroy",
                    fillcolor="rgba(200,155,60,0.08)",
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#9b9892", family="DM Sans"),
                    margin=dict(l=20, r=20, t=10, b=30),
                    height=280,
                    xaxis=dict(showgrid=False, color="#6c6a64"),
                    yaxis=dict(gridcolor="#2a2a30", color="#6c6a64"),
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption(s.summary)


# ---------------------------------------------------------------------------
# Tab — Workspace (overview / management)
# ---------------------------------------------------------------------------

with tab_workspace:
    styles.rule_heading("Knowledge Base Overview")
    docs = list(st.session_state.doc_index.values())
    total_chunks = sum(d.get("chunks", 0) for d in docs)
    total_words = sum((d.get("approx_words") or 0) for d in docs)

    cols = st.columns(3)
    with cols[0]:
        styles.stat_card("Documents", str(len(docs)), "indexed sources")
    with cols[1]:
        styles.stat_card("Knowledge Chunks", f"{total_chunks:,}", "retrievable passages")
    with cols[2]:
        styles.stat_card("Approx. Words", f"{total_words:,}", "across all documents")

    styles.rule_heading("AI Stack")
    st.markdown(
        f'<div class="card">'
        f'<div class="card-title">Generation Model</div>'
        f'<div class="card-meta" style="font-size:0.82rem; line-height:1.7; color:var(--text-dim);">'
        f'<strong style="color:var(--accent);">LLM:</strong> {LLM_MODEL} via Ollama (local inference)<br>'
        f'<strong style="color:var(--accent);">Embeddings:</strong> BAAI/bge-small-en-v1.5 (sentence-transformers, on-device)<br>'
        f'<strong style="color:var(--accent);">Vector Store:</strong> ChromaDB (persistent, encrypted on-disk)'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    styles.danger_zone(
        "Permanently deletes all indexed documents and clears the vector store. "
        "This action cannot be undone."
    )
    if st.button("Reset Workspace", type="primary"):
        store.reset()
        st.session_state.doc_index = {}
        st.session_state.messages = []
        st.session_state.uploaded_blobs = {}
        st.session_state.active_doc_ids = []
        for k in list(st.session_state.keys()):
            if k.startswith("trends_") or k == "cdq":
                st.session_state.pop(k, None)
        st.toast("Workspace reset.")
        st.rerun()