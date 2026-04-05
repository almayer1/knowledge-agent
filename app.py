from fastapi import FastAPI, HTTPException
from rich.panel import Panel
from rich.text import Text
from rich import print
import typer

from exceptions import OllamaConnectionError, EmptyKnowledgeBaseError, UnsupportedFileTypeError, EmptyFileError
from config import Settings
from models import AskRequest
from ingest import load_document, chunk_document
from store import count, add_chunks
from generator import generate




app = FastAPI(
    title="Knowledge Agent API",
    description="Query your personal knowledge base"
)

@app.post("/ingest")
def ingest():
    pass

@app.post("/ask")
def ask(request: AskRequest):
     # if question empty
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Please enter a question.")

    try:
        answer = generate(request.question)
    except OllamaConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except EmptyKnowledgeBaseError as e:
        raise HTTPException(status_code=503, detail=str(e))
    
    return answer


@app.get("/stats")
def stats():
    pass