from fastapi import APIRouter, Depends, status, UploadFile, File
from pymongo.database import Database
from typing import Dict, Any

from app.schemas.paper_schema import PaperResponse
from app.services import paper_service
from app.database.mongodb import get_database
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/projects/{project_id}/papers", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
def upload_paper(
    project_id: str,
    file: UploadFile = File(...),
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload a new PDF paper to a project.
    """
    return paper_service.upload_paper(db, project_id, current_user["_id"], file)

@router.get("/projects/{project_id}/papers")
def get_project_papers(
    project_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all papers in a project.
    """
    return paper_service.get_project_papers(db, project_id, current_user["_id"])

@router.get("/papers/{paper_id}", response_model=PaperResponse)
def get_paper(
    paper_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get paper metadata.
    """
    return paper_service.get_paper_by_id(db, paper_id, current_user["_id"])

@router.delete("/papers/{paper_id}")
def delete_paper(
    paper_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a paper and its associated file.
    """
    return paper_service.delete_paper(db, paper_id, current_user["_id"])
