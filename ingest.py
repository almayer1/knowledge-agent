from pathlib import Path
import math
import hashlib
import pdfplumber

from config import Settings
from models import Document, DocType, Chunk
from ocr import read_handwritten_pdf

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

def read_pdf(path: Path) -> Document:
    # Extract text
    with pdfplumber.open(path) as pdf:
        text = pdf.pages[0].extract_text() or ""
    
    # Check if typed or handwritten
    if len(text.strip()) > 50:       
        return read_typed_pdf(path)  
    else:                            
        return read_handwritten_pdf(path)
    
def read_typed_pdf(path: Path) -> Document:
    path = path.resolve()

    # Extract text from each page
    all_text = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() 
            all_text.append(f"[Page {i+1}]\n{text}")
    
    # Combine each page's text
    full_text = "\n".join(all_text)

    return Document(
        id=hashlib.md5(str(path).encode()).hexdigest(),
        source=path,
        content=full_text,
        doc_type=DocType.TYPED_PDF
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
    
READERS = {
    ".txt": read_txt,
    ".pdf": read_pdf
}

def load_document(path: Path) -> Document:
    # Get what type of file it is
    extension = path.suffix.lower()

    # Determine what file reader to use and use it
    return READERS[extension](path)