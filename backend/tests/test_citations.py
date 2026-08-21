import pytest
from app.services.citation_service import CitationManager

def test_citation_manager_deduplication():
    cm = CitationManager()
    
    chunks = [
        {"paper_id": "p1", "chunk_id": "c1", "faiss_id": "f1", "page_number": 1, "text": "A"},
        {"paper_id": "p1", "chunk_id": "c1", "faiss_id": "f1", "page_number": 1, "text": "A"},
        {"paper_id": "p2", "chunk_id": "c2", "faiss_id": "f2", "page_number": 2, "text": "B"}
    ]
    
    formatted = cm.register_chunks(chunks)
    
    # Check deduplication
    assert len(cm.sources) == 2
    assert formatted[0]["citation_id"] == 1
    assert formatted[1]["citation_id"] == 1
    assert formatted[2]["citation_id"] == 2

def test_validate_citations_valid():
    cm = CitationManager()
    chunks = [
        {"paper_id": "p1", "chunk_id": "c1", "faiss_id": "f1", "page_number": 1, "text": "A"},
        {"paper_id": "p2", "chunk_id": "c2", "faiss_id": "f2", "page_number": 2, "text": "B"}
    ]
    cm.register_chunks(chunks)
    
    text = "The paper says A [1]. Also B [2]."
    cleaned, sources = cm.validate_citations(text)
    
    assert cleaned == "The paper says A [1]. Also B [2]."
    assert len(sources) == 2
    assert sources[0]["citation_id"] == "1"
    assert sources[1]["citation_id"] == "2"

def test_validate_citations_invalid_stripped():
    cm = CitationManager()
    chunks = [
        {"paper_id": "p1", "chunk_id": "c1", "faiss_id": "f1", "page_number": 1, "text": "A"}
    ]
    cm.register_chunks(chunks)
    
    text = "Valid [1]. Hallucinated [2]. Another [3, 1]."
    cleaned, sources = cm.validate_citations(text)
    
    assert cleaned == "Valid [1]. Hallucinated. Another [1]."
    assert len(sources) == 1
    assert sources[0]["citation_id"] == "1"

def test_validate_citations_no_evidence():
    cm = CitationManager()
    # No registered chunks
    text = "It uses Adam optimizer [1]."
    cleaned, sources = cm.validate_citations(text)
    
    assert cleaned == "It uses Adam optimizer."
    assert len(sources) == 0
