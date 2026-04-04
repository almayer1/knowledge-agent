from pathlib import Path
import math
import hashlib

from config import Settings
from models import Document, DocType, Chunk

settings = Settings()

def read_txt(path: Path) -> Document:
    path = path.resolve()
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return Document(
        id=hashlib.md5(str(path).encode()).hexdigest(),
        source=str(path),
        content=content,
        doc_type=DocType.TEXT
    )

def chunk_document(document: Document) -> list[Chunk]:
    #find total number of chunks
    step = settings.chunk_size - settings.chunk_overlap
    total_chunks = math.ceil((len(document.content) / step))
    
    #loop through document total_chunks times breaking document into chunks
    chunks = []
    for i in range(total_chunks):
        start = i * step
        end = start + settings.chunk_size
        chunk_content = document.content[start:end]
        chunk = Chunk(
            id=f"{document.id}_chunk_{i}",
            document_id=document.id,
            content=chunk_content,
            metadata={
                "source": document.source,
                "doc_type": document.doc_type,
                "chunk_index": i,
                "total_chunks": total_chunks,
                "document_id": document.id
            }
        )
        chunks.append(chunk)
    return chunks
    