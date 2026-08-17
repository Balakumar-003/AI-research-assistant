from fastapi import HTTPException, status
from pymongo.database import Database
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.models.chunk_model import create_chunk_document
from app.schemas.chunk_schema import ChunkingStatsResponse, PaginatedChunksResponse, ChunkResponse
from app.services.paper_service import validate_object_id

def serialize_chunk(chunk) -> ChunkResponse:
    return ChunkResponse(
        chunk_id=str(chunk["_id"]),
        paper_id=chunk["paper_id"],
        chunk_index=chunk["chunk_index"],
        page_start=chunk["page_start"],
        page_end=chunk["page_end"],
        text=chunk["text"]
    )

def generate_chunks(db: Database, paper_id: str, user_id: str) -> ChunkingStatsResponse:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
        
    if paper.get("status") != "processed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Paper text extraction is not complete")

    # Update status to chunking
    db.papers.update_one({"_id": paper_obj_id}, {"$set": {"chunking_status": "chunking", "updated_at": datetime.utcnow()}})

    try:
        # Fetch pages in order
        pages_cursor = db.document_pages.find({"paper_id": paper_id}).sort("page_number", 1)
        pages = list(pages_cursor)
        
        if not pages:
            raise ValueError("No text available for chunking. OCR may be required.")
            
        full_text = ""
        page_mappings = []  # List of (start_offset, end_offset, page_number)
        
        for p in pages:
            text = p.get("text", "")
            if not text:
                continue
                
            start_offset = len(full_text)
            full_text += text + "\n\n"
            end_offset = len(full_text)
            
            page_mappings.append((start_offset, end_offset, p["page_number"]))
            
        if not full_text.strip():
            raise ValueError("No text available for chunking. OCR may be required.")

        # Setup Splitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        chunk_texts = splitter.split_text(full_text)
        
        # Delete existing chunks idempotently
        db.document_chunks.delete_many({"paper_id": paper_id})
        
        chunks_to_insert = []
        search_idx = 0
        
        for idx, c_text in enumerate(chunk_texts):
            # Find offset
            chunk_start = full_text.find(c_text, search_idx)
            if chunk_start == -1:
                chunk_start = search_idx # Fallback if slightly modified
            chunk_end = chunk_start + len(c_text)
            
            # Map to pages
            page_start = None
            page_end = None
            for (m_start, m_end, p_num) in page_mappings:
                if page_start is None and m_start <= chunk_start < m_end:
                    page_start = p_num
                if m_start < chunk_end <= m_end:
                    page_end = p_num
            
            if page_start is None and page_mappings:
                page_start = page_mappings[0][2]
            if page_end is None:
                page_end = page_start
                
            chunk_doc = create_chunk_document(
                paper_id=paper_id,
                project_id=paper["project_id"],
                user_id=user_id,
                chunk_index=idx,
                text=c_text,
                page_start=page_start,
                page_end=page_end
            )
            chunks_to_insert.append(chunk_doc)
            search_idx = chunk_start + max(1, len(c_text) - settings.CHUNK_OVERLAP)
            
        chunk_count = len(chunks_to_insert)
        if chunk_count > 0:
            db.document_chunks.insert_many(chunks_to_insert)
            
        # Update status
        db.papers.update_one(
            {"_id": paper_obj_id}, 
            {"$set": {"chunking_status": "completed", "chunk_count": chunk_count, "updated_at": datetime.utcnow()}}
        )
        
        return ChunkingStatsResponse(
            message="Paper chunked successfully",
            paper_id=paper_id,
            chunk_count=chunk_count,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            status="completed"
        )

    except Exception as e:
        db.papers.update_one(
            {"_id": paper_obj_id}, 
            {"$set": {"chunking_status": "failed", "updated_at": datetime.utcnow()}}
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Chunking failed: {str(e)}")


def get_paper_chunks(db: Database, paper_id: str, user_id: str, page: int = 1, limit: int = 20) -> PaginatedChunksResponse:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
        
    skip = (page - 1) * limit
    chunks_cursor = db.document_chunks.find({"paper_id": paper_id}).sort("chunk_index", 1).skip(skip).limit(limit)
    total = db.document_chunks.count_documents({"paper_id": paper_id})
    
    return PaginatedChunksResponse(
        paper_id=paper_id,
        total=total,
        chunks=[serialize_chunk(c) for c in chunks_cursor]
    )

def get_chunk(db: Database, chunk_id: str, user_id: str) -> ChunkResponse:
    chunk_obj_id = validate_object_id(chunk_id)
    chunk = db.document_chunks.find_one({"_id": chunk_obj_id, "user_id": user_id})
    if not chunk:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chunk not found")
    return serialize_chunk(chunk)

def delete_paper_chunks(db: Database, paper_id: str, user_id: str) -> dict:
    paper_obj_id = validate_object_id(paper_id)
    paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id})
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")
        
    db.document_chunks.delete_many({"paper_id": paper_id})
    db.papers.update_one({"_id": paper_obj_id}, {"$set": {"chunking_status": "not_started", "chunk_count": 0}})
    
    return {"message": "Chunks deleted successfully"}
