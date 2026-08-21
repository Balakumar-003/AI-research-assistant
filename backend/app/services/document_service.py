import os
# pyrefly: ignore [missing-import]
import pymupdf
from fastapi import HTTPException, status
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
import re

from app.schemas.paper_schema import ProcessPaperResponse, ProcessingStatusResponse, PaginatedContentResponse, PageItem
from app.services.paper_service import validate_object_id

def clean_extracted_text(text: str) -> str:
    """
    Perform safe, minimal cleaning of extracted PDF text.
    - Normalize repeated whitespace
    - Remove unnecessary leading/trailing spaces
    - Remove excessive blank lines
    """
    if not text:
        return ""
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple blank lines into max 2 blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Collapse multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def process_pdf(db: Database, paper_id: str, user_id: str) -> ProcessPaperResponse:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
        
    if paper.get("status") == "processed":
        return ProcessPaperResponse(
            message="Paper already processed",
            paper_id=paper_id,
            status=paper["status"],
            page_count=paper.get("page_count")
        )
        
    # Update status to processing
    db.papers.update_one({"_id": paper_obj_id}, {"$set": {"status": "processing", "updated_at": datetime.utcnow()}})
    
    file_path = paper.get("file_path")
    if not file_path or not os.path.exists(file_path):
        db.papers.update_one({"_id": paper_obj_id}, {"$set": {"status": "failed", "error_message": "File not found on disk"}})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File not found on disk")
        
    try:
        doc = pymupdf.open(file_path)
        page_count = doc.page_count
        
        # We will delete any existing pages if this is a re-process
        db.document_pages.delete_many({"paper_id": paper_id})
        
        pages_to_insert = []
        for i in range(page_count):
            page = doc[i]
            text = page.get_text("text")
            cleaned_text = clean_extracted_text(text)
            
            page_doc = {
                "paper_id": paper_id,
                "project_id": paper["project_id"],
                "user_id": user_id,
                "page_number": i + 1,  # 1-indexed
                "text": cleaned_text,
                "has_text": bool(cleaned_text),
                "created_at": datetime.utcnow()
            }
            pages_to_insert.append(page_doc)
            
        if pages_to_insert:
            db.document_pages.insert_many(pages_to_insert)
            
        doc.close()
        
        # Update paper to processed
        db.papers.update_one(
            {"_id": paper_obj_id}, 
            {"$set": {"status": "processed", "page_count": page_count, "updated_at": datetime.utcnow()}}
        )
        
        return ProcessPaperResponse(
            message="Paper processed successfully",
            paper_id=paper_id,
            status="processed",
            page_count=page_count
        )
        
    except Exception as e:
        db.papers.update_one({"_id": paper_obj_id}, {"$set": {"status": "failed", "error_message": str(e)}})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Processing failed: {str(e)}")

def get_processing_status(db: Database, paper_id: str, user_id: str) -> ProcessingStatusResponse:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
        
    return ProcessingStatusResponse(
        paper_id=paper_id,
        status=paper.get("status", "uploaded"),
        page_count=paper.get("page_count")
    )

def get_paper_content(db: Database, paper_id: str, user_id: str, page: int = 1, limit: int = 10) -> PaginatedContentResponse:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
        
    skip = (page - 1) * limit
    pages_cursor = db.document_pages.find({"paper_id": paper_id}).sort("page_number", 1).skip(skip).limit(limit)
    
    total_pages_count = db.document_pages.count_documents({"paper_id": paper_id})
    
    pages_list = []
    for p in pages_cursor:
        pages_list.append(PageItem(
            page_number=p["page_number"],
            text=p.get("text", ""),
            has_text=p.get("has_text", False)
        ))
        
    return PaginatedContentResponse(
        paper_id=paper_id,
        pages=pages_list,
        total_pages=total_pages_count,
        current_page=page,
        limit=limit
    )
