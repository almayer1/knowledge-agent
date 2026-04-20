# Personal Knowledge Agent

A RAG-based AI assistant that ingests your notes and documents, stores them in a vector database, and answers questions about your own knowledge base — with source citations.

Built for students who use **GoodNotes** — export your handwritten lecture notes as PDFs and ask questions about them instantly. Also supports typed PDFs, textbooks, and plain text files.

---

## What it does

- **Ingests** `.txt` and `.pdf` files (typed and handwritten) from a local folder
- **OCRs** handwritten GoodNotes PDF exports using Apple Vision on macOS
- **Auto-detects** whether a PDF has a text layer or needs OCR — no manual sorting required
- **Chunks** documents into overlapping pieces for precise vector search
- **Stores** chunks in ChromaDB as semantic vectors — persists to disk between sessions
- **Retrieves** the 5 most relevant chunks for any question using cosine similarity
- **Generates** grounded answers using a local LLM (Ollama) with inline source citations
- **Exposes** a REST API via FastAPI for programmatic access
- **Provides** a Streamlit frontend with file upload, query interface, and source display
- **Handles errors** gracefully — empty folders, unsupported files, Ollama not running, corrupted PDFs

---

## Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Core language |
| ChromaDB | Local persistent vector database |
| Ollama (llama3.2) | Local LLM — runs fully on your machine, no API costs |
| ollama (Python) | Native Python client for Ollama |
| Apple Vision | Handwriting OCR for GoodNotes exports |
| pdfplumber | Text extraction for typed PDFs |
| pdf2image | PDF page rendering for OCR pipeline |
| FastAPI | REST API layer |
| Streamlit | Web frontend with file upload and query UI |
| Pydantic | Data validation and settings management |
| Typer | CLI interface |
| Rich | Terminal output formatting |
| pytest | Test suite |

---

## Architecture

```
data/raw/
   ├── lecture_notes.pdf    (GoodNotes export - handwritten)
   ├── databases.pdf        (typed PDF - lecture slides)
   └── notes.txt            (plain text)
          |
          v
     ingest.py
     ├── Auto-detects file type via READERS dispatch table
     ├── Typed PDF   -> pdfplumber text extraction
     ├── Handwritten PDF -> Apple Vision OCR (ocr.py)
     └── .txt -> direct read
          |
          v
     chunk_document()
     Overlapping 500-char chunks with 50-char overlap
     Each chunk carries source, page, position metadata
          |
          v
     ChromaDB (data/chroma/)
     Cosine similarity vector store — persists between sessions
          |
     On query:
          |
          v
     retriever.py
     Semantic search — finds top 5 relevant chunks
     Formats as labeled context: [Source 1: file.pdf]
          |
          v
     generator.py
     Assembles prompt: system rules + context + question
     Calls Ollama (llama3.2) locally
          |
          v
     Answer with inline citations [Source 1], [Source 2]...
```

---

## Setup

### Prerequisites

- macOS (Apple Vision OCR is macOS only)
- [Ollama](https://ollama.com) installed
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/knowledge-agent.git
cd knowledge-agent
```

### 2. Install dependencies

```bash
uv sync
brew install poppler
```

### 3. Pull the LLM

```bash
ollama pull llama3.2
```

### 4. Configure settings

Create a `.env` file in the project root:

```bash
LLM_MODEL=llama3.2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
OCR_DPI=300
OCR_MIN_CONFIDENCE=0.65
API_URL=http://localhost:8000
```

No API keys required. Everything runs locally.

---

## Usage

### Streamlit UI

The easiest way to use the agent. Starts Ollama, the FastAPI backend, and Streamlit frontend in one command:

```bash
make run
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

- **Upload files** via drag and drop in the sidebar
- **Click ENCODE INTO VAULT** to ingest them
- **Type a question** and click TRANSMIT
- **Expand SOURCE NODES** to see which documents were cited

To stop both servers:

```bash
make stop
```

---

### REST API

Start the FastAPI server:

```bash
uv run uvicorn app:app --reload
```

Interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs)

**Ingest documents:**
```bash
curl -X POST http://localhost:8000/ingest
```

**Ask a question:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is a database schema?"}'
```

**Check stats:**
```bash
curl http://localhost:8000/stats
```

---

### CLI

**Add a single file:**

```bash
uv run python -m main add-file /path/to/notes.pdf
```

**Ingest all files in data/raw/:**

```bash
uv run python -m main ingest
```

```
╭───────────── Summary ─────────────╮
│ 50 chunks were added from 5 files │
╰───────────────────────────────────╯
```

**Ask a question:**

```bash
uv run python -m main ask "what is the difference between Europe and the US on data privacy?"
```

```
╭──────────────────────── Knowledge Agent ────────────────────────╮
│ In Europe, citizens have a right to be forgotten, meaning they  │
│ can request personal data to be deleted [Source 1]. In contrast,│
│ the United States has no explicit right to deletion [Source 1]. │
│                                                                  │
│ Key Points:                                                      │
│ - Europe: GDPR gives citizens right to delete their data        │
│ - US: no equivalent explicit privacy right exists               │
╰──────────────────────────────────────────────────────────────────╯
Sources:
  [Source 1] databases.pdf
  [Source 2] databases.pdf
```

**Check knowledge base size:**

```bash
uv run python -m main stats
```

---

## GoodNotes Workflow

1. Open GoodNotes and select your notebook
2. Tap **Export -> PDF**
3. Run `uv run python -m main add-file /path/to/export.pdf`
4. Ask questions about your lecture notes

> **Note:** A confidence warning appears if OCR quality is low (below 65%). This usually means the handwriting was unclear or the PDF was a low quality scan — double check that content manually.

> **Tip:** If your GoodNotes PDF exports clean text via pdfplumber (digital stylus notes), the system automatically skips OCR and uses direct text extraction instead — faster and 100% accurate.

---

## Error Handling

The system handles common failure cases gracefully:

| Situation | Behaviour |
|---|---|
| `data/raw/` is empty | Warns and exits cleanly |
| Unsupported file type in folder | Skips file, warns, continues |
| File has bad encoding | Skips file, warns, continues |
| Empty or corrupted PDF | Skips file, warns, continues |
| Ollama not running | Clear error with fix instructions |
| Empty knowledge base on query | Tells user to run ingest first |
| Empty question string | Prompts user to enter a question |
| chunk_overlap >= chunk_size | Caught at startup by Pydantic validator |
| API unreachable from UI | Connection error shown in Streamlit |

---

## Project Structure

```
knowledge-agent/
├── config.py          — settings loaded from .env with Pydantic validation
├── models.py          — data shapes: Document, Chunk, QueryResult, Answer
├── exceptions.py      — custom exceptions: OllamaConnectionError, EmptyKnowledgeBaseError etc.
├── ingest.py          — file readers, auto-detection dispatch table, chunker
├── ocr.py             — Apple Vision OCR pipeline for handwritten PDFs
├── store.py           — ChromaDB operations: add, query, count
├── retriever.py       — semantic search and context formatting
├── generator.py       — prompt assembly and Ollama LLM call
├── main.py            — Typer CLI: ingest, ask, stats, add-file
├── app.py             — FastAPI REST API: /ingest, /ask, /stats
├── streamlit_app.py   — Streamlit web UI
├── Makefile           — make run / make stop
├── data/
│   ├── raw/           — drop your documents here
│   └── chroma/        — vector database (auto-generated, gitignored)
└── tests/
    ├── conftest.py       — shared pytest fixtures
    ├── test_ingest.py    — chunking and ingestion tests
    └── test_retriever.py — context formatting tests
```

---

## Configuration

All settings can be overridden in `.env`:

| Setting | Default | Description |
|---|---|---|
| `LLM_MODEL` | `llama3.2` | Ollama model to use |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | Ollama server URL |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks (must be < CHUNK_SIZE) |
| `TOP_K` | `5` | Chunks retrieved per query |
| `OCR_DPI` | `300` | PDF render resolution for OCR |
| `OCR_MIN_CONFIDENCE` | `0.65` | Confidence threshold for OCR quality warning |
| `API_URL` | `http://localhost:8000` | FastAPI server URL for Streamlit |

---

## Testing

```bash
uv run pytest tests/ -v
```

```
tests/test_ingest.py::test_chunk_count          PASSED
tests/test_ingest.py::test_chunk_overlap        PASSED
tests/test_ingest.py::test_chunk_metadata_keys  PASSED
tests/test_ingest.py::test_consistent_ids       PASSED
tests/test_retriever.py::test_return_type       PASSED
tests/test_retriever.py::test_source_labels     PASSED
tests/test_retriever.py::test_chunk_content     PASSED
tests/test_retriever.py::test_sources_formatting PASSED

8 passed in 1.27s
```

---

## Key Concepts

**RAG (Retrieval-Augmented Generation)** — instead of asking the LLM to answer from memory (where it hallucinates), relevant chunks are first retrieved from the vector database and passed as context. The LLM reasons over your actual notes.

**Chunking with overlap** — documents are split into ~500 character pieces with 50 character overlap at boundaries. Overlap prevents answers from being cut in half at chunk edges.

**Cosine similarity** — ChromaDB finds relevant chunks by measuring the angle between vectors. Semantically similar text produces similar vectors even if the exact words differ. "What makes cells produce energy?" finds mitochondria notes without those exact words appearing.

**Auto-detection** — PDFs are automatically routed to the right reader. pdfplumber checks for a text layer first. If found, it extracts directly. If not (GoodNotes handwriting), Apple Vision OCR is used.

**Upsert** — re-ingesting the same file updates existing chunks rather than creating duplicates. Safe to run ingest as many times as you want.

---

## Roadmap

- [x] `add-file` CLI command — copy and ingest a single file in one step
- [x] FastAPI REST API
- [x] Streamlit web UI with drag and drop upload
- [ ] Incremental ingestion — skip already ingested files for speed
- [ ] Markdown file support
- [ ] Conversation memory for follow-up questions
- [ ] Re-ranking for improved retrieval quality
- [ ] Answer logging and stats dashboard
