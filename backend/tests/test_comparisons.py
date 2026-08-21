import pytest
from app.agents.comparison_graph import parse_comparison_request, validate_papers

@pytest.mark.asyncio
async def test_parse_comparison_request_empty():
    state = {"dimensions": [], "query": None}
    new_state = await parse_comparison_request(state)
    assert len(new_state["dimensions"]) > 0
    assert "Methodology" in new_state["dimensions"]

@pytest.mark.asyncio
async def test_validate_papers_insufficient():
    state = {"paper_ids": ["paper1"], "errors": []}
    new_state = await validate_papers(state)
    assert len(new_state["errors"]) > 0
    assert "two papers" in new_state["errors"][0]

@pytest.mark.asyncio
async def test_validate_papers_duplicates():
    state = {"paper_ids": ["paper1", "paper1"], "errors": []}
    new_state = await validate_papers(state)
    assert len(new_state["errors"]) > 0
    assert "Duplicate" in new_state["errors"][-1]
