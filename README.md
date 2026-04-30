# DocuAgent AI — Secure Document Intelligence Platform

A NotebookLM-style RAG application that runs entirely on your MacBook with enterprise-grade security. Built on **Ollama (llama3:8b)**, **ChromaDB**, and **Streamlit**. No data ever leaves your machine — complete privacy by design.

## What it does

- **Ingest anything securely** — PDF, DOCX, XLSX, CSV, PPTX, EPUB, HTML, Markdown, JSON, plain text, or any URL. All data stays on your machine.
- **Chat with verifiable citations** — answers cite the sources with similarity scores and exact passages. Perfect for regulated workflows and legal review.
- **Auto-generated briefings** — map-reduce summaries work on long documents within an 8B model's context.
- **Suggested questions** — both single-document starter questions and *cross-document* questions that compare or combine multiple sources.
- **Entity & theme analysis** — extract people, organizations, places, dates, and themes from any document.
- **Trend detection** — automatically charts every numeric column in a spreadsheet with one-line interpretation.
- **Focus mode** — restrict retrieval to specific documents for tight scope and document segregation.
- **Zero cloud exposure** — workspace lives on disk, nothing is sent to any remote service. Compliant by default.

## Setup (Mac)

### 1. Install Ollama and pull the model

```bash
brew install ollama
ollama serve &           # leave running in a background tab
ollama pull llama3:8b
```

> **Tip — Apple Silicon:** llama3:8b runs at ~30–40 tokens/sec on an M2/M3 with 16GB RAM. If you have 8GB, prefer `llama3.2:3b` and set `RAG_LLM_MODEL=llama3.2:3b` before launching.

### 2. Install Python dependencies

```bash
cd RAGmodel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run will download the embedding model (~130 MB).

### 3. Launch

```bash
streamlit run app.py
```

Open the URL it prints (usually `http://localhost:8501`).

## Configuration

All knobs live in `core/config.py` and can also be set via environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `RAG_LLM_MODEL` | `llama3:8b` | Ollama model tag for generation |
| `RAG_EMBED_MODEL` | `BAAI/bge-small-en-v1.5` | sentence-transformers model for embeddings |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                     Streamlit UI                     │
│  ┌──────────┬──────────┬──────────┬────────────────┐ │
│  │   Chat   │ Summary  │ Analysis │     Trends     │ │
│  └──────────┴──────────┴──────────┴────────────────┘ │
└──────────────────────────────────────────────────────┘
            │                              │
            ▼                              ▼
   ┌─────────────────┐            ┌──────────────────┐
   │   RAG engine    │            │     Analyzer     │
   │ retrieve + gen  │            │ summary/entities │
   └─────────────────┘            └──────────────────┘
            │                              │
            ▼                              ▼
   ┌─────────────────┐            ┌──────────────────┐
   │   ChromaDB      │            │      Ollama      │
   │ (local, on-disk)│            │  (llama3:8b)     │
   └─────────────────┘            └──────────────────┘
            ▲
            │
   ┌─────────────────┐
   │ Document parser │
   │ pdf/docx/xlsx/… │
   └─────────────────┘
```

## File layout

```
RAGmodel/
├── app.py                        # Streamlit entry point
├── core/
│   ├── config.py                 # paths, models, security thresholds
│   ├── document_processor.py     # multi-format parsing + secure chunking
│   ├── rag_engine.py             # ChromaDB + Ollama integration
│   └── analyzer.py               # summary, entities, trends, questions
├── ui/
│   └── styles.py                 # injected CSS for professional look
├── .streamlit/config.toml        # Streamlit theme
├── .data/                        # auto-created — vectors, uploads (local only)
├── requirements.txt
├── README.md
└── BUSINESS_PITCH.md             # how to sell this
```

## Troubleshooting

**"Ollama unreachable"** — run `ollama serve` in a terminal and confirm `curl http://localhost:11434/api/tags` returns JSON.

**"model 'llama3:8b' is not pulled"** — run `ollama pull llama3:8b`.

**Slow first response** — the embedding model loads on first query. Subsequent ones are fast.

**Long PDFs feel truncated in summaries** — the map-reduce summary uses the first 8 batches by design (to fit in an 8B model's working memory). For deep dives into later chapters, use Focus mode and ask targeted questions.

**OCR for scanned PDFs** — install Tesseract: `brew install tesseract poppler`. The current parser will then fall back to OCR for image-only PDFs (extension hook included; wire it in if you need it).
