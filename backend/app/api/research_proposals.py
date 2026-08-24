from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from app.services.auth_service import get_current_user
from app.database.connection import get_db
from pymongo.database import Database
from app.schemas.research_proposal_schemas import (
    ResearchProposalRequest,
    ResearchProposalResponse
)
from app.services.research_proposal_service import research_proposal_service

router = APIRouter(prefix="/workspaces/{workspace_id}/research-proposals", tags=["Research Proposals"])

@router.post("", response_model=ResearchProposalResponse)
async def generate_research_proposal(
    workspace_id: str,
    request: ResearchProposalRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    if request.project_id != workspace_id:
        request.project_id = workspace_id
    
    return await research_proposal_service.generate_proposal(
        db=db,
        user_id=current_user["uid"],
        request=request
    )

@router.get("", response_model=List[Any])
def list_research_proposals(
    workspace_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return research_proposal_service.list_proposals(
        db=db,
        user_id=current_user["uid"],
        project_id=workspace_id
    )

@router.get("/{proposal_id}", response_model=ResearchProposalResponse)
def get_research_proposal(
    workspace_id: str,
    proposal_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return research_proposal_service.get_proposal(
        db=db,
        user_id=current_user["uid"],
        proposal_id=proposal_id
    )
