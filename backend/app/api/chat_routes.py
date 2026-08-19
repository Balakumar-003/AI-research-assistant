import json
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pymongo.database import Database
from typing import Dict, Any, Optional

from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.rag.rag_pipeline import run_rag_query
from app.database.mongodb import get_database
from app.core.dependencies import get_current_user
from app.services import chat_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    stream: bool = Query(False, description="Whether to stream the response via SSE"),
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if not stream:
        result = await run_rag_query(
            user_id=str(current_user["_id"]),
            question=request.question,
            project_id=request.project_id,
            paper_id=request.paper_id,
            top_k=request.top_k,
            db=db
        )
        return ChatResponse(**result)
    else:
        # For simplicity in this milestone, if stream=True, we yield chunks of the final answer.
        # A fully implemented SSE streaming route requires a generator that calls the LLM.
        # We will fallback to running it normally and sending it chunk by chunk for now.
        async def mock_stream():
            result = await run_rag_query(
                user_id=str(current_user["_id"]),
                question=request.question,
                project_id=request.project_id,
                paper_id=request.paper_id,
                top_k=request.top_k,
                db=db
            )
            yield f"data: {json.dumps(result)}\n\n"
        return StreamingResponse(mock_stream(), media_type="text/event-stream")

@router.get("/chat/history")
def get_chat_history(
    project_id: Optional[str] = None,
    limit: int = 50,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    history = chat_service.get_recent_history(
        db=db,
        user_id=str(current_user["_id"]),
        project_id=project_id,
        limit=limit
    )
    # Exclude _id or map to string
    for h in history:
        h["_id"] = str(h["_id"])
    return {"history": history}
