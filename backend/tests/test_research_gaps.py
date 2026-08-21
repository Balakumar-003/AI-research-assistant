import pytest
import unittest.mock as mock
from app.agents.research_gap_graph import validate_gaps, generate_candidate_gaps, ResearchGapState
from app.services.citation_service import CitationManager

@pytest.mark.asyncio
async def test_validate_gaps_strong_evidence():
    state: ResearchGapState = {
        "candidate_gaps": [
            {
                "gap_id": "g1",
                "statement": "Multilingual evaluation remains limited compared with English-only evaluation.",
                "supporting_evidence": [{"paper_id": "p1", "text": "We evaluated on English."}, {"paper_id": "p2", "text": "English dataset used."}],
                "counter_evidence": []
            }
        ],
        "citation_manager": CitationManager(),
        "errors": []
    }
    
    # Mock LLM to return VALIDATED
    from app.services.llm_service import llm_service
    with mock.patch.object(llm_service, 'generate', return_value=('{"status": "VALIDATED", "refined_statement": "Multilingual evaluation is limited.", "importance": "HIGH", "confidence": "HIGH"}', None)):
        new_state = await validate_gaps(state)
        
    assert len(new_state["validated_gaps"]) == 1
    assert len(new_state["rejected_gaps"]) == 0
    assert new_state["validated_gaps"][0]["confidence"] == "HIGH"
    assert new_state["validated_gaps"][0]["importance"] == "HIGH"

@pytest.mark.asyncio
async def test_validate_gaps_false_gap_rejected():
    state: ResearchGapState = {
        "candidate_gaps": [
            {
                "gap_id": "g1",
                "statement": "No multilingual research exists.",
                "supporting_evidence": [],
                "counter_evidence": [{"paper_id": "p3", "text": "We evaluate on English, Spanish, and French datasets."}]
            }
        ],
        "citation_manager": CitationManager(),
        "errors": []
    }
    
    # Mock LLM to return REJECTED due to counter-evidence
    from app.services.llm_service import llm_service
    with mock.patch.object(llm_service, 'generate', return_value=('{"status": "REJECTED"}', None)):
        new_state = await validate_gaps(state)
        
    assert len(new_state["validated_gaps"]) == 0
    assert len(new_state["rejected_gaps"]) == 1
    assert "errors" in new_state
    assert len(new_state["errors"]) > 0
    assert "No sufficiently supported research gaps" in new_state["errors"][0]
