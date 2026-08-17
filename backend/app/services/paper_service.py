import os
import shutil
from fastapi import UploadFile, HTTPException, status
from pymongo.database import Database
from bson import ObjectId
from bson.errors import InvalidId

from app.schemas.paper_schema import PaperResponse
from app.models.paper_model import create_paper_document

UPLOAD_DIR = "uploads"

def validate_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID format"
        )

def serialize_paper(paper) -> PaperResponse:
    paper["id"] = str(paper.pop("_id"))
    return PaperResponse(**paper)

def upload_paper(db: Database, project_id: str, user_id: str, file: UploadFile) -> PaperResponse:
    if not file.filename.endswith(".pdf") or file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
        
    project_obj_id = validate_object_id(project_id)
    project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id, "is_active": True})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )
        
    # Ensure upload directory exists
    project_upload_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_upload_dir, exist_ok=True)
    
    file_path = os.path.join(project_upload_dir, file.filename)
    
    # Check if file already exists in this project
    existing_paper = db.papers.find_one({"project_id": project_id, "filename": file.filename})
    if existing_paper:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A paper with this filename already exists in the project"
        )

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
        
    paper_doc = create_paper_document(file.filename, file_path, project_id, user_id)
    result = db.papers.insert_one(paper_doc)
    paper_doc["_id"] = result.inserted_id
    
    return serialize_paper(paper_doc)

def get_project_papers(db: Database, project_id: str, user_id: str) -> dict:
    project_obj_id = validate_object_id(project_id)
    project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id, "is_active": True})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized"
        )
        
    papers_cursor = db.papers.find({"project_id": project_id, "user_id": user_id})
    papers = [serialize_paper(p) for p in papers_cursor]
    return {"papers": papers, "total": len(papers)}

def get_paper_by_id(db: Database, paper_id: str, user_id: str) -> PaperResponse:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    return serialize_paper(paper)

def delete_paper(db: Database, paper_id: str, user_id: str) -> dict:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
        
    # Delete from file system
    file_path = paper.get("file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        
    # Delete from DB
    db.papers.delete_one({"_id": paper_obj_id})
    db.document_pages.delete_many({"paper_id": paper_id})
    
    return {"message": "Paper deleted successfully"}
