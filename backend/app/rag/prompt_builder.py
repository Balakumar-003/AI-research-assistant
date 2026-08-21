import json
from typing import List, Dict, Any

def get_system_instructions() -> str:
    return """You are a highly capable AI Research Assistant.
Your task is to answer the user's question using ONLY the provided document chunks.

CRITICAL INSTRUCTIONS:
1. Grounding: You MUST NOT use your pre-training knowledge to answer the question. If the provided chunks do not contain enough information to fully answer the question, clearly state "I couldn't find relevant content in your uploaded papers for this question." Do not guess or hallucinate.
2. Output Format: You MUST output valid JSON ONLY, with no markdown formatting around it. The JSON must match this exact structure:
{
    "answer": "Your detailed answer goes here. When using information from the sources, append the citation ID inline, e.g., [1] or [1, 2]."
}
3. Citations: If you use information from a source, you MUST cite its SOURCE_ID inline in the answer text using square brackets like [1]. Do not invent citations. Do not include a separate citations list in the JSON.
"""

def build_rag_prompt(question: str, formatted_context: str, chat_history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
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
    if not formatted_context:
        context_text += "No relevant chunks found.\n\n"
    else:
        context_text += formatted_context
            
    prompt_content = f"{context_text}\n\nUser Question: {question}"
    messages.append({"role": "user", "content": prompt_content})
    
    return messages
