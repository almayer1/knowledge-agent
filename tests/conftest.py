import pytest

from models import Document, DocType

@pytest.fixture
def sample_document():
    return Document(
        id="123445678901234567",
        source="data/raw/lecture.txt",
        content="A" * 600 + "B" * 600,
        doc_type=DocType.TEXT
    )