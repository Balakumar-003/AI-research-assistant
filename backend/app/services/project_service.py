from pymongo.database import Database
from pymongo import ReturnDocument
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from typing import List
from datetime import datetime

from app.schemas.project_schema import CreateProjectRequest, UpdateProjectRequest, ProjectResponse
from app.models.project_model import create_project_document

def validate_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid project ID format"
        )

def serialize_project(project) -> ProjectResponse:
    project["id"] = str(project.pop("_id"))
    return ProjectResponse(**project)

def create_project(db: Database, user_id: str, request: CreateProjectRequest) -> ProjectResponse:
    project_doc = create_project_document(
        name=request.name.strip(),
        description=request.description.strip() if request.description else None,
        user_id=user_id
    )
    result = db.projects.insert_one(project_doc)
    project_doc["_id"] = result.inserted_id
    return serialize_project(project_doc)

def get_user_projects(db: Database, user_id: str) -> dict:
    projects_cursor = db.projects.find({"user_id": user_id, "is_active": True})
    projects = [serialize_project(p) for p in projects_cursor]
    return {"projects": projects, "total": len(projects)}

def get_project_by_id(db: Database, project_id: str, user_id: str) -> ProjectResponse:
    obj_id = validate_object_id(project_id)
    project = db.projects.find_one({"_id": obj_id, "user_id": user_id, "is_active": True})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return serialize_project(project)

def update_project(db: Database, project_id: str, user_id: str, request: UpdateProjectRequest) -> ProjectResponse:
    if request.name is None and request.description is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided for update"
        )
        
    obj_id = validate_object_id(project_id)
    
    # Check if project exists and belongs to user
    existing_project = db.projects.find_one({"_id": obj_id, "user_id": user_id, "is_active": True})
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    update_data = {"updated_at": datetime.utcnow()}
    if request.name is not None:
        update_data["name"] = request.name.strip()
    if request.description is not None:
        update_data["description"] = request.description.strip()
        
    updated_project = db.projects.find_one_and_update(
        {"_id": obj_id, "user_id": user_id, "is_active": True},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )
    
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    return serialize_project(updated_project)

def delete_project(db: Database, project_id: str, user_id: str) -> dict:
    obj_id = validate_object_id(project_id)
    
    # Check if project exists and belongs to user
    existing_project = db.projects.find_one({"_id": obj_id, "user_id": user_id, "is_active": True})
    if not existing_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
        
    # Soft delete
    db.projects.update_one(
        {"_id": obj_id, "user_id": user_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Project deleted successfully"}
