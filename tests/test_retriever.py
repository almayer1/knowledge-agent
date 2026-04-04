import pytest

from retriever import format_context

#format_context
def test_return_type(sample_query_results):
    results = format_context(sample_query_results)
    assert isinstance(results, str)

def test_source_labels(sample_query_result):
    results = [sample_query_result, sample_query_result, sample_query_result]
    context = format_context(results)
    assert "[Source 1:" in context
    assert "[Source 2:" in context
    assert "[Source 3:" in context

def test_chunk_content(sample_query_results):
    context = format_context(sample_query_results)
    content = sample_query_results[0].chunk.content
    assert content in context

def test_sources_formatting(sample_query_result):
    results = [sample_query_result, sample_query_result, sample_query_result]
    context = format_context(results)
    assert "[Source 1:" in context
    assert "[Source 2:" in context
    assert context.index("[Source 1:" ) < context.index("[Source 2:")
    
