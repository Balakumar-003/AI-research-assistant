import json
import logging
from fastapi import APIRouter, Depends
from typing import Dict, Any
from langchain_core.messages import HumanMessage, ToolMessage

from app.schemas.agent_schemas import AgentRequest, AgentResponse
from app.agents.graph import agent_graph
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/agent", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    
    # Initialize state
    initial_state = {
        "question": request.question,
        "user_id": user_id,
        "project_id": request.project_id,
        "paper_ids": request.paper_ids,
        "messages": [HumanMessage(content=request.question)],
        "iteration_count": 0,
        "final_answer": None,
        "sources": [],
        "tools_used": []
    }
    
    # Run graph
    try:
        final_state = await agent_graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return AgentResponse(
            answer="An error occurred while processing your request.",
            status="error"
        )
        
    # Extract sources from tool results
    sources = []
    for msg in final_state.get("messages", []):
        if isinstance(msg, ToolMessage):
            try:
                content = json.loads(msg.content)
                if content.get("success") and "results" in content:
                    for r in content["results"]:
                        sources.append({
                            "paper_id": r.get("paper_id"),
                            "page": r.get("page_number"),
                            "chunk_id": r.get("chunk_id"),
                            "score": r.get("score")
                        })
            except:
                pass
                
    # Deduplicate sources
    seen_chunks = set()
    unique_sources = []
    for s in sources:
        if s["chunk_id"] not in seen_chunks:
            seen_chunks.add(s["chunk_id"])
            unique_sources.append(s)
            
    return AgentResponse(
        answer=final_state.get("final_answer") or "I could not generate an answer.",
        sources=unique_sources,
        tools_used=list(set(final_state.get("tools_used", []))),
        status="completed"
    )
