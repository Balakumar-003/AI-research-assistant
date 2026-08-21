import pytest
from app.agents.literature_review_graph import parse_research_question, select_relevant_papers

@pytest.mark.asyncio
async def test_parse_research_question():
    state = {"query": "What are the latest techniques in RAG?"}
    new_state = await parse_research_question(state)
    assert "scope" in new_state
    assert len(new_state["scope"]) > 0

@pytest.mark.asyncio
async def test_select_relevant_papers_no_papers():
    # If no papers match because mock returns nothing or max papers is tiny
    state = {
        "user_id": "test_user",
        "project_id": "test_proj",
        "query": "test query",
        "paper_ids": [],
        "max_papers": 5,
        "errors": []
    }
    
    # Mock embedding provider to avoid loading model
    from app.providers.embedding_provider import embedding_provider
    import unittest.mock as mock
    with mock.patch.object(embedding_provider, 'embed_query', return_value=[0.1] * 384):
        new_state = await select_relevant_papers(state)
        
    assert "relevant_paper_ids" in new_state
    if not new_state["relevant_paper_ids"]:
        assert len(new_state["errors"]) > 0
