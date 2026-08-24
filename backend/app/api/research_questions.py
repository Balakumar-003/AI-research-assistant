from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from app.services.auth_service import get_current_user
from app.database.connection import get_db
from pymongo.database import Database
from app.schemas.research_question_schemas import (
    ResearchQuestionRequest,
    ResearchQuestionRecordResponse,
    ResearchQuestionHistoryItem
)
from app.services.research_question_service import research_question_service

router = APIRouter(prefix="/workspaces/{workspace_id}/research-questions", tags=["Research Questions"])

@router.post("/generate", response_model=ResearchQuestionRecordResponse)
async def generate_research_questions(
    workspace_id: str,
    request: ResearchQuestionRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    if request.project_id != workspace_id:
        request.project_id = workspace_id
    
    return await research_question_service.run_generation(
        db=db,
        user_id=current_user["uid"],
        request=request
    )

@router.get("", response_model=List[ResearchQuestionHistoryItem])
def get_research_questions_history(
    workspace_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return research_question_service.get_project_generations(
        db=db,
        user_id=current_user["uid"],
        project_id=workspace_id
    )

@router.get("/{question_set_id}", response_model=ResearchQuestionRecordResponse)
def get_research_question_set(
    workspace_id: str,
    question_set_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return research_question_service.get_generation(
        db=db,
        user_id=current_user["uid"],
        question_set_id=question_set_id
    )

@router.patch("/{question_set_id}/select/{question_id}", response_model=ResearchQuestionRecordResponse)
def select_primary_research_question(
    workspace_id: str,
    question_set_id: str,
    question_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return research_question_service.select_primary_question(
        db=db,
        user_id=current_user["uid"],
        question_set_id=question_set_id,
        question_id=question_id
    )
