from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pymongo.database import Database

from app.core.dependencies import get_current_user
from app.database.mongodb import get_database
from app.schemas.literature_review_schemas import LiteratureReviewRequest, LiteratureReviewRecordResponse, LiteratureReviewHistoryItem
from app.services.literature_review_service import literature_review_service

router = APIRouter()

@router.post("/", response_model=LiteratureReviewRecordResponse)
async def create_literature_review(
    request: LiteratureReviewRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Creates a new automated literature review.
    """
    return await literature_review_service.run_review(db, str(current_user["_id"]), request)

@router.get("/{review_id}", response_model=LiteratureReviewRecordResponse)
def get_literature_review(
    review_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    Get a specific literature review result.
    """
    return literature_review_service.get_review(db, str(current_user["_id"]), review_id)

@router.get("/project/{project_id}", response_model=List[LiteratureReviewHistoryItem])
def get_project_literature_reviews(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    """
    List literature reviews for a project.
    """
    return literature_review_service.get_project_reviews(db, str(current_user["_id"]), project_id)
