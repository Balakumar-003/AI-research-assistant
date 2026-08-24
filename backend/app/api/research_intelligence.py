from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.services.auth_service import get_current_user
from app.database.connection import get_db
from app.schemas.research_goal_schemas import ResearchGoalCreate, ResearchGoalResponse
from app.services.research_intelligence_service import research_intelligence_service

router = APIRouter(prefix="/workspaces/{workspace_id}/research-goals", tags=["Research Intelligence"])

@router.post("", response_model=ResearchGoalResponse)
def create_and_analyze_goal(
    workspace_id: str,
    request: ResearchGoalCreate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    if request.project_id != workspace_id:
        request.project_id = workspace_id
        
    return research_intelligence_service.create_and_analyze_goal(
        db=db,
        user_id=current_user["uid"],
        request=request
    )

@router.get("/{goal_id}", response_model=ResearchGoalResponse)
def get_goal(
    workspace_id: str,
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return research_intelligence_service.get_goal(
        db=db,
        user_id=current_user["uid"],
        goal_id=goal_id
    )
