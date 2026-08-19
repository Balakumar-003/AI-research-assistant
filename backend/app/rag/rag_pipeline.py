import logging
import json
from typing import Dict, Any, Optional

from app.core.config import settings
from app.providers.embedding_provider import embedding_provider
from app.services.vector_service import vector_store
from app.rag.prompt_builder import build_rag_prompt
from app.services.llm_service import llm_service
from app.services import chat_service

logger = logging.getLogger(__name__)

async def run_rag_query(
    user_id: str,
    question: str,
    project_id: Optional[str] = None,
    paper_id: Optional[str] = None,
    top_k: int = 6,
    db: Any = None
) -> dict:
    # 1. Embed query
    query_embedding = embedding_provider.embed_query(question)
    
    # 2. Retrieve chunks
    chunks = await vector_store.search(
        query_embedding=query_embedding,
        top_k=top_k,
        user_id=user_id,
        paper_id=paper_id
    )
    
    # 3. Guardrail check
    if not chunks or chunks[0].get("score", 0) < settings.RETRIEVAL_SCORE_THRESHOLD:
        logger.info(f"Guardrail triggered. Top score: {chunks[0].get('score', 0) if chunks else 0}")
        response_data = {
            "answer": "I couldn't find relevant content in your uploaded papers for this question.",
            "citations": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0}
        }
        if db:
            chat_service.save_turn(db, user_id, project_id, question, response_data["answer"], response_data["citations"], response_data["usage"])
        return response_data
        
    # 4. Load history
    chat_history = []
    if db:
        chat_history = chat_service.get_recent_history(db, user_id, project_id, limit=settings.CHAT_HISTORY_TURNS)
        
    # 5. Build prompt
    messages = build_rag_prompt(question, chunks, chat_history)
    
    # 6 & 7. Call LLM & Parse
    def _parse_llm_response(text: str) -> dict:
        try:
            # Clean up markdown formatting if the LLM leaked it
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return None

    # First attempt
    llm_response, usage = await llm_service.generate(messages)
    parsed_data = _parse_llm_response(llm_response)
    
    if not parsed_data:
        # Retry once
        logger.warning("Failed to parse LLM JSON. Retrying.")
        retry_msg = {"role": "user", "content": "You must output valid JSON only. Try again."}
        messages.append({"role": "assistant", "content": llm_response})
        messages.append(retry_msg)
        
        llm_response2, usage2 = await llm_service.generate(messages)
        usage["prompt_tokens"] += usage2.get("prompt_tokens", 0)
        usage["completion_tokens"] += usage2.get("completion_tokens", 0)
        
        parsed_data = _parse_llm_response(llm_response2)
        if not parsed_data:
            logger.error("Failed to parse LLM JSON on retry.")
            parsed_data = {
                "answer": "I encountered an error generating a structured response.",
                "citations": []
            }
            
    parsed_data["usage"] = usage
    
    # 8. Save and Return
    if db:
        chat_service.save_turn(
            db, 
            user_id, 
            project_id, 
            question, 
            parsed_data.get("answer", ""), 
            parsed_data.get("citations", []), 
            usage
        )
        
    return parsed_data
