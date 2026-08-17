from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from typing import Dict, Any

from app.schemas.project_schema import CreateProjectRequest, UpdateProjectRequest, ProjectResponse
from app.services import project_service
from app.database.mongodb import get_database
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: CreateProjectRequest, 
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new research project.
    """
    return project_service.create_project(db, current_user["_id"], request)

@router.get("/projects")
def get_projects(
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Return all active projects belonging to the authenticated user.
    """
    return project_service.get_user_projects(db, current_user["_id"])

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a single project by ID for the authenticated user.
    """
    return project_service.get_project_by_id(db, project_id, current_user["_id"])

@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update a project's name or description.
    """
    return project_service.update_project(db, project_id, current_user["_id"], request)

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Soft delete a project.
    """
    return project_service.delete_project(db, project_id, current_user["_id"])
