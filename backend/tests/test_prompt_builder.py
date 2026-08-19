from app.rag.prompt_builder import build_rag_prompt

def test_build_rag_prompt_formats_chunks():
    chunks = [
        {"paper_id": "p1", "page_number": 1, "section": "Intro", "text": "This is chunk 1."}
    ]
    messages = build_rag_prompt("What is it?", chunks, [])
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "CRITICAL INSTRUCTIONS:" in messages[0]["content"]
    assert "valid JSON ONLY" in messages[0]["content"]
    
    assert messages[1]["role"] == "user"
    assert "[Source 1]" in messages[1]["content"]
    assert "Paper: p1" in messages[1]["content"]
    assert "This is chunk 1." in messages[1]["content"]
    assert "What is it?" in messages[1]["content"]

def test_build_rag_prompt_includes_history():
    history = [
        {"question": "Q1", "answer": "A1"}
    ]
    messages = build_rag_prompt("Q2", [], history)
    
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Q1"
    assert messages[2]["role"] == "assistant"
    assert messages[2]["content"] == "A1"
    assert messages[3]["role"] == "user"
    assert "No relevant chunks found" in messages[3]["content"]
    assert "User Question: Q2" in messages[3]["content"]
