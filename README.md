# Personal Knowledge Agent

A RAG-based AI assistant that ingests your notes and documents, stores them in a vector database, and answers questions about your own knowledge base — with source citations.

Built to work with **GoodNotes exports**, typed PDFs, and plain text files. Ask questions about your lecture notes and get grounded answers that cite exactly where the information came from.

---

## What it does

- **Ingests** `.txt` and `.pdf` files (typed and handwritten) from a local folder
- **OCRs** handwritten GoodNotes PDF exports using Apple Vision
- **Auto-detects** whether a PDF has a text layer or needs OCR
- **Chunks** documents into overlapping pieces for precise vector search
- **Stores** chunks in ChromaDB as semantic vectors
- **Retrieves** the most relevant chunks for any question
- **Generates** grounded answers using a local LLM (Ollama) with source citations

---

## Stack

| Tool | Purpose |
|---|---|
| Python 3.12 | Core language |
| ChromaDB | Local vector database |
| Ollama (llama3.2) | Local LLM — runs fully on your machine |
| Apple Vision | Handwriting OCR for GoodNotes exports |
| pdfplumber | Text extraction for typed PDFs |
| pdf2image | PDF page rendering for OCR |
| Pydantic | Data validation and settings management |
| Typer | CLI interface |
| Rich | Terminal output formatting |

---

## Architecture

```
data/raw/
   ├── lecture_notes.pdf    (GoodNotes export)
   ├── textbook.pdf         (typed PDF)
   └── notes.txt            (plain text)
          |
          v
     ingest.py
     ├── Auto-detects file type
     ├── Typed PDF  -> pdfplumber text extraction
     ├── Handwritten PDF -> Apple Vision OCR
     └── .txt -> direct read
          |
          v
     chunk_document()
     Splits text into overlapping 500-char chunks
          |
          v
     ChromaDB (data/chroma/)
     Stores chunks as semantic vectors
          |
     On query:
          |
          v
     retriever.py
     Finds top 5 most relevant chunks by cosine similarity
          |
          v
     generator.py
     Builds prompt: system instructions + context + question
     Sends to Ollama (llama3.2)
          |
          v
     Answer with citations [Source 1], [Source 2]...
```

---

## Setup

### Prerequisites

- macOS (Apple Vision OCR is macOS only)
- [Ollama](https://ollama.com) installed and running
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/knowledge-agent.git
cd knowledge-agent
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Install system dependencies

```bash
brew install poppler
```

### 4. Pull the LLM

```bash
ollama pull llama3.2
ollama serve
```

### 5. Configure settings

Create a `.env` file in the project root:

```bash
LLM_MODEL=llama3.2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=5
OCR_DPI=300
OCR_MIN_CONFIDENCE=0.65
```

No API keys required. Everything runs locally on your machine.

---

## Usage

### Ingest your documents

Drop your files into `data/raw/` then run:

```bash
uv run python -m main ingest
```

```
╭───────────── Summary ─────────────╮
│ 50 chunks were added from 5 files │
╰───────────────────────────────────╯
```

Supported formats:
- `.txt` — plain text notes
- `.pdf` — typed PDFs (lecture slides, textbooks) and handwritten GoodNotes exports

### Ask a question

```bash
uv run python -m main ask "what are the key constraints in a relational database?"
```

```
╭──────────────────────── Knowledge Agent ────────────────────────╮
│ Answer:                                                          │
│ Key constraints ensure uniqueness in a relational schema        │
│ [Source 1]. Candidate keys are all possible unique identifiers  │
│ and the primary key is chosen from those candidates [Source 2]. │
│                                                                  │
│ Key Points:                                                      │
│ • Key constraints provide uniqueness                            │
│ • Candidate keys -> Primary key selection                       │
│                                                                  │
│ Sources Used: [Source 1][Source 2]                              │
╰──────────────────────────────────────────────────────────────────╯
Sources:
  [Source 1] data/raw/databases.pdf
  [Source 2] data/raw/databases.pdf
```

### Check how many chunks are stored

```bash
uv run python -m main stats
```

```
╭─────── Stats ───────╮
│ There Are 50 Chunks │
╰─────────────────────╯
```

### Add more documents

Drop new files into `data/raw/` and run ingest again. Existing documents are upserted — no duplicates.

---

## GoodNotes Workflow

1. Open GoodNotes and select your notebook
2. Tap **Export -> PDF**
3. Save the file to `data/raw/`
4. Run `uv run python -m main ingest`
5. Ask questions about your lecture notes

> **Note:** A confidence warning will appear if OCR quality is low (below 65%). This means the handwriting was difficult to read — double check that content manually.

---

## Project Structure

```
knowledge-agent/
├── config.py       — settings loaded from .env
├── models.py       — Pydantic data shapes (Document, Chunk, QueryResult, Answer)
├── ingest.py       — file readers, auto-detection, chunking
├── ocr.py          — Apple Vision OCR pipeline for handwritten PDFs
├── store.py        — ChromaDB vector store operations
├── retriever.py    — semantic search and context formatting
├── generator.py    — prompt assembly and LLM call
├── main.py         — Typer CLI (ingest, ask, stats)
├── data/
│   ├── raw/        — drop your documents here
│   └── chroma/     — vector database (auto-generated, not tracked)
└── tests/
    ├── test_ingest.py
    └── test_retriever.py
```

---

## Configuration

All settings can be overridden in `.env`:

| Setting | Default | Description |
|---|---|---|
| `LLM_MODEL` | `llama3.2` | Ollama model to use |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | Ollama server URL |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K` | `5` | Chunks retrieved per query |
| `OCR_DPI` | `300` | PDF render resolution for OCR |
| `OCR_MIN_CONFIDENCE` | `0.65` | Confidence threshold for OCR warning |

---

## Key Concepts

**RAG (Retrieval-Augmented Generation)** — instead of asking the LLM to answer from memory, relevant chunks are first retrieved from the vector database and passed as context. The LLM reasons over your actual notes rather than making things up.

**Chunking with overlap** — documents are split into ~500 character pieces with 50 character overlap at boundaries. Overlap prevents answers from being cut in half at chunk edges.

**Cosine similarity** — ChromaDB finds relevant chunks by measuring the angle between vectors. Semantically similar text produces similar vectors even if the exact words differ.

**Auto-detection** — PDFs are automatically routed to the right reader. If pdfplumber finds a text layer it uses that directly. If not, Apple Vision OCR is used instead.

---

## Roadmap

- [ ] Markdown file support
- [ ] Conversation memory for follow-up questions
- [ ] Streamlit chat UI
- [ ] Async ingestion for large document collections
- [ ] Usage logging and stats dashboard
- [ ] Re-ranking for improved retrieval quality
