"""Central configuration for the RAG workstation."""
from pathlib import Path
import os

# ---------- Models ----------
# Generation model — Ollama tag. llama3:8b is the user's request.
LLM_MODEL = os.getenv("RAG_LLM_MODEL", "llama3:8b")

# Embeddings — using sentence-transformers locally (no Ollama dependency for embeddings,
# faster on Mac CPUs and produces stable vectors). Swap to "nomic-embed-text" via Ollama
# if you prefer a single runtime.
EMBED_MODEL = os.getenv("RAG_EMBED_MODEL", "BAAI/bge-small-en-v1.5")

# Ollama host
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# ---------- Storage ----------
APP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = APP_ROOT / ".data"
VECTOR_DIR = DATA_DIR / "chroma"
UPLOAD_DIR = DATA_DIR / "uploads"
NOTES_DIR = DATA_DIR / "notes"

for d in (DATA_DIR, VECTOR_DIR, UPLOAD_DIR, NOTES_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---------- Chunking ----------
CHUNK_SIZE = 900           # characters
CHUNK_OVERLAP = 150
MAX_CONTEXT_CHUNKS = 6     # how many chunks to feed the LLM

# ---------- Generation ----------
GENERATION_TEMPERATURE = 0.2
SUMMARY_TEMPERATURE = 0.3
ANALYSIS_TEMPERATURE = 0.4

# ---------- UI ----------
APP_NAME = "DocuAgent"
APP_TAGLINE = "Secure AI Document Intelligence"
SUPPORTED_EXTENSIONS = [
    "pdf", "docx", "txt", "md", "csv", "xlsx", "xls",
    "pptx", "html", "htm", "epub", "json"
]
