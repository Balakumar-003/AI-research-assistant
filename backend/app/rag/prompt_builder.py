import json
from typing import List, Dict, Any

def get_system_instructions() -> str:
    return """You are a highly capable AI Research Assistant.
Your task is to answer the user's question using ONLY the provided document chunks.

CRITICAL INSTRUCTIONS:
1. Grounding: You MUST NOT use your pre-training knowledge to answer the question. If the provided chunks do not contain enough information to fully answer the question, clearly state "I couldn't find relevant content in your uploaded papers for this question." Do not guess or hallucinate.
2. Output Format: You MUST output valid JSON ONLY, with no markdown formatting around it. The JSON must match this exact structure:
{
    "answer": "Your detailed answer goes here.",
    "citations": [
        {
            "source_index": 1,
            "paper": "Paper Name",
            "page": 2,
            "section": "Section Name if available"
        }
    ]
}
3. Citations: If you use information from a source chunk, you must include it in the `citations` list. The `source_index` should match the index provided in the chunk label (e.g., [Source 1]). If you do not use any chunks (e.g., you say you couldn't find relevant content), the `citations` list should be empty.
"""

def build_rag_prompt(question: str, retrieved_chunks: List[Dict[str, Any]], chat_history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Constructs the message array for the LLM.
    """
    messages = [
        {"role": "system", "content": get_system_instructions()}
    ]
    
    # Add chat history
    for turn in chat_history:
        messages.append({"role": "user", "content": turn.get("question", "")})
        messages.append({"role": "assistant", "content": turn.get("answer", "")})
        
    # Format current question and chunks
    context_text = "Here are the relevant document chunks:\n\n"
    if not retrieved_chunks:
        context_text += "No relevant chunks found.\n\n"
    else:
        for i, chunk in enumerate(retrieved_chunks, 1):
            paper_id = chunk.get('paper_id', 'Unknown')
            page = chunk.get('page_number', 0)
            section = chunk.get('section', '')
            text = chunk.get('text', '')
            
            context_text += f"[Source {i}] (Paper: {paper_id}, Page: {page}, Section: {section})\n{text}\n\n"
            
    prompt_content = f"{context_text}\n\nUser Question: {question}"
    messages.append({"role": "user", "content": prompt_content})
    
    return messages
