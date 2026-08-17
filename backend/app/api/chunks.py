from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from typing import Dict, Any

from app.schemas.chunk_schema import ChunkingStatsResponse, PaginatedChunksResponse, ChunkResponse
from app.services import chunk_service
from app.database.mongodb import get_database
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/papers/{paper_id}/chunks", response_model=ChunkingStatsResponse)
def generate_chunks(
    paper_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate chunks for a processed paper.
    """
    return chunk_service.generate_chunks(db, paper_id, current_user["_id"])

@router.get("/papers/{paper_id}/chunks", response_model=PaginatedChunksResponse)
def get_paper_chunks(
    paper_id: str,
    page: int = 1,
    limit: int = 20,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List all chunks for a paper.
    """
    return chunk_service.get_paper_chunks(db, paper_id, current_user["_id"], page, limit)

@router.get("/chunks/{chunk_id}", response_model=ChunkResponse)
def get_chunk(
    chunk_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific chunk.
    """
    return chunk_service.get_chunk(db, chunk_id, current_user["_id"])

@router.delete("/papers/{paper_id}/chunks")
def delete_paper_chunks(
    paper_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete chunks for a paper.
    """
    return chunk_service.delete_paper_chunks(db, paper_id, current_user["_id"])
