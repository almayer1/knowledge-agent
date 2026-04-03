from pathlib import Path
import hashlib

from config import Settings
from models import Document, DocType, Chunk

def read_txt(path: Path) -> Document:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return Document(
        id=hashlib.md5(str(path).encode()).hexdigest(),
        source=str(path),
        content=content,
        doc_type=DocType.TEXT
    )

    