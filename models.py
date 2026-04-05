from pydantic import BaseModel
from enum import Enum

class DocType(str, Enum):
    TEXT = "txt"
    MARKDOWN = "md"
    TYPED_PDF = "typed_pdf"
    HANDWRITTEN_PDF = "handwritten_pdf"

class Document(BaseModel):
    id: str
    source: str
    content: str
    doc_type: DocType
    ocr_confidence: float | None = None

class Chunk(BaseModel):
    id: str
    document_id: str
    content: str
    metadata: dict

class QueryResult(BaseModel):
    chunk: Chunk
    score: float

class Answer(BaseModel):
    question: str
    answer: str
    sources: list[QueryResult]

class AskRequest(BaseModel):
    question: str
    history: list = []

class IngestResponse(BaseModel):
    chunks_added: int
    files_processed: int
    warnings: list[str] = []

class StatsResponse(BaseModel):
    chunk_count: int