import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.rag.rag_pipeline import run_rag_query

@pytest.mark.asyncio
@patch("app.rag.rag_pipeline.vector_store")
@patch("app.rag.rag_pipeline.embedding_provider")
async def test_run_rag_query_guardrail(mock_embedding, mock_vector_store):
    # Mock embedding
    mock_embedding.embed_query.return_value = [0.1]
    
    # Mock search returning a low score
    mock_vector_store.search = AsyncMock(return_value=[{"score": 0.1, "chunk_id": "c1"}])
    
    # Run
    result = await run_rag_query("user1", "What is testing?")
    
    # Guardrail should trigger
    assert "couldn't find relevant content" in result["answer"]
    assert len(result["citations"]) == 0

@pytest.mark.asyncio
@patch("app.rag.rag_pipeline.llm_service")
@patch("app.rag.rag_pipeline.vector_store")
@patch("app.rag.rag_pipeline.embedding_provider")
async def test_run_rag_query_success(mock_embedding, mock_vector_store, mock_llm_service):
    # Mock embedding
    mock_embedding.embed_query.return_value = [0.1]
    
    # Mock search returning a high score
    mock_vector_store.search = AsyncMock(return_value=[
        {"score": 0.9, "chunk_id": "c1", "paper_id": "p1", "text": "Test"}
    ])
    
    # Mock LLM returning valid JSON
    mock_llm_service.generate = AsyncMock(return_value=(
        '{"answer": "Test answer", "citations": [{"source_index": 1, "paper": "p1", "page": 1, "section": ""}]}',
        {"prompt_tokens": 10, "completion_tokens": 20}
    ))
    
    result = await run_rag_query("user1", "What is testing?")
    
    assert result["answer"] == "Test answer"
    assert len(result["citations"]) == 1
    assert result["citations"][0]["paper"] == "p1"
    assert result["usage"]["prompt_tokens"] == 10

@pytest.mark.asyncio
@patch("app.rag.rag_pipeline.llm_service")
@patch("app.rag.rag_pipeline.vector_store")
@patch("app.rag.rag_pipeline.embedding_provider")
async def test_run_rag_query_retry_on_bad_json(mock_embedding, mock_vector_store, mock_llm_service):
    # Mock embedding
    mock_embedding.embed_query.return_value = [0.1]
    
    # Mock search returning a high score
    mock_vector_store.search = AsyncMock(return_value=[
        {"score": 0.9, "chunk_id": "c1", "paper_id": "p1", "text": "Test"}
    ])
    
    # First response is bad JSON, second is good
    mock_llm_service.generate = AsyncMock(side_effect=[
        ("Bad JSON", {"prompt_tokens": 5, "completion_tokens": 5}),
        ('{"answer": "Retried answer", "citations": []}', {"prompt_tokens": 10, "completion_tokens": 10})
    ])
    
    result = await run_rag_query("user1", "What is testing?")
    
    assert result["answer"] == "Retried answer"
    assert result["usage"]["prompt_tokens"] == 15
