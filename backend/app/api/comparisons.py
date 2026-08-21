from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pymongo.database import Database

from app.core.dependencies import get_current_user
from app.database.mongodb import get_database
from app.schemas.comparison_schemas import ComparisonRequest, ComparisonRecordResponse, ComparisonHistoryItem
from app.services.comparison_service import comparison_service

router = APIRouter()

@router.post("/", response_model=ComparisonRecordResponse)
async def create_comparison(
    request: ComparisonRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Creates a new multi-paper comparison.
    """
    return await comparison_service.run_comparison(db, str(current_user["_id"]), request)

@router.get("/{comparison_id}", response_model=ComparisonRecordResponse)
def get_comparison(
    comparison_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Get a specific comparison result.
    """
    return comparison_service.get_comparison(db, str(current_user["_id"]), comparison_id)

@router.get("/project/{project_id}", response_model=List[ComparisonHistoryItem])
def get_project_comparisons(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    List comparisons for a project.
    """
    return comparison_service.get_project_comparisons(db, str(current_user["_id"]), project_id)
