import pytest

from models import Document, DocType, Chunk, QueryResult

@pytest.fixture
def sample_document():
    return Document(
        id="757471ee32681c3aa5e93ae225905564",
        source="data/raw/lecture.txt",
        content="A" * 600 + "B" * 600,
        doc_type=DocType.TEXT
    )

@pytest.fixture
def sample_query_results(sample_query_result) -> list[QueryResult]:
    return [sample_query_result]

@pytest.fixture
def sample_query_result(sample_chunk: Chunk) -> QueryResult:
    return QueryResult(
        chunk=sample_chunk,
        score=0.8
    )

@pytest.fixture
def sample_chunk() -> Chunk:
    return Chunk(
        id="757471ee32681c3aa5e93ae225905564_chunk_1",
        document_id="757471ee32681c3aa5e93ae225905564",
        content="A" * 500,
        metadata={
            "source": "data/raw/lecture.txt",
            "doc_type": DocType.TEXT,
            "chunk_index": 1,
            "total_chunks": 3,
            "document_id": "757471ee32681c3aa5e93ae225905564"
        }

    )