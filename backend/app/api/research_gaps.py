from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pymongo.database import Database

from app.core.dependencies import get_current_user
from app.database.mongodb import get_database
from app.schemas.research_gap_schemas import ResearchGapRequest, ResearchGapRecordResponse, ResearchGapHistoryItem
from app.services.research_gap_service import research_gap_service

router = APIRouter()

@router.post("/", response_model=ResearchGapRecordResponse)
async def create_research_gap_analysis(
    request: ResearchGapRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Creates a new research gap analysis.
    """
    return await research_gap_service.run_discovery(db, str(current_user["_id"]), request)

@router.get("/{analysis_id}", response_model=ResearchGapRecordResponse)
def get_research_gap_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Get a specific research gap analysis result.
    """
    return research_gap_service.get_analysis(db, str(current_user["_id"]), analysis_id)

@router.get("/project/{project_id}", response_model=List[ResearchGapHistoryItem])
def get_project_research_gaps(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    List research gap analyses for a project.
    """
    return research_gap_service.get_project_analyses(db, str(current_user["_id"]), project_id)
