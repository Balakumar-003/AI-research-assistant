import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.services.citation_service import CitationManager
from app.services.summarization_service import SummarizationService

@pytest.mark.asyncio
@patch('app.services.summarization_service.llm_service')
async def test_summarization_service_map_reduce(mock_llm_service):
    # Mock LLM generation to just echo back dummy summaries
    async def mock_generate(messages):
        # Determine if it's map or reduce based on system prompt
        system_prompt = messages[0]["content"]
        if "extract key information" in system_prompt:
            return "Intermediate summary with citation [1].", {"prompt_tokens": 10, "completion_tokens": 5}
        else:
            return "Final synthesized summary using [1].", {"prompt_tokens": 20, "completion_tokens": 10}
            
    mock_llm_service.generate.side_effect = mock_generate
    
    cm = CitationManager()
    summarizer = SummarizationService(cm)
    
    # 25 chunks to force multiple batches (batch_size = 10 -> 3 batches)
    chunks = [
        {"paper_id": "p1", "chunk_id": f"c{i}", "faiss_id": f"f{i}", "page_number": 1, "text": f"Text {i}"}
        for i in range(25)
    ]
    
    final_summary = await summarizer.summarize(chunks, summary_type="standard")
    
    # Check that map was called 3 times, reduce 1 time (total 4 calls)
    assert mock_llm_service.generate.call_count == 4
    
    # Check final summary output
    assert final_summary == "Final synthesized summary using [1]."
    
    # Ensure CitationManager registered all chunks
    assert len(cm.sources) == 25
    assert cm.next_citation_id == 26

@pytest.mark.asyncio
async def test_summarization_service_empty():
    cm = CitationManager()
    summarizer = SummarizationService(cm)
    
    final_summary = await summarizer.summarize([], summary_type="standard")
    assert final_summary == "No content available to summarize."
