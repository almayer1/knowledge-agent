import pytest

from ingest import chunk_document

def test_chunk_count(sample_document):
    chunks = chunk_document(sample_document)
    assert len(chunks) == 3

def test_chunk_overlap(sample_document):
    chunks = chunk_document(sample_document)
    assert chunks[0].content[-50:] == chunks[1].content[:50]
    
def test_chunk_metadata_keys(sample_document):
    chunks = chunk_document(sample_document)
    for chunk in chunks:
        assert 'source' in chunk.metadata
        assert 'doc_type' in chunk.metadata
        assert 'chunk_index' in chunk.metadata
        assert 'total_chunks' in chunk.metadata
        assert 'document_id' in chunk.metadata

def test_consistent_ids(sample_document):
    a = chunk_document(sample_document)
    b = chunk_document(sample_document)
    assert len(a) == len(b)
    for i in range(len(a)):
        assert a[i].id == b[i].id
        assert a[i].document_id == b[i].document_id
    
