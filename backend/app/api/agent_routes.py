import json
import logging
from fastapi import APIRouter, Depends
from typing import Dict, Any
from langchain_core.messages import HumanMessage, ToolMessage

from app.schemas.agent_schemas import AgentRequest, AgentResponse
from app.agents.graph import agent_graph
from app.core.dependencies import get_current_user
from app.services.citation_service import CitationManager
from app.agents.tools import citation_manager_ctx

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/agent", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    
    # Initialize CitationManager for this request
    cm = CitationManager()
    token = citation_manager_ctx.set(cm)
    
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
        citation_manager_ctx.reset(token)
        return AgentResponse(
            answer="An error occurred while processing your request.",
            status="error"
        )
        
    # Validate citations and clean up the answer
    raw_answer = final_state.get("final_answer") or "I could not generate an answer."
    validated_answer, validated_sources = cm.validate_citations(raw_answer)
    
    citation_manager_ctx.reset(token)
            
    return AgentResponse(
        answer=validated_answer,
        sources=validated_sources,
        tools_used=list(set(final_state.get("tools_used", []))),
        status="completed"
    )
