from pathlib import Path

from models import QueryResult
from store import query

def retrieve(question: str) -> list[QueryResult]:
    return query(question)

def format_context(results: list[QueryResult]) -> str:
    parts = []

    for i, result in enumerate(results):
        path = Path(result.chunk.metadata["source"])
        parts.append(f"[Source {i + 1}: {path.name}\n{result.chunk.content}")
    
    return "\n\n".join(parts)