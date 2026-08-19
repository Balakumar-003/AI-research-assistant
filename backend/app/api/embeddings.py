from fastapi import APIRouter, Depends
from pymongo.database import Database
from typing import Dict, Any

from app.schemas.embedding_schema import EmbeddingStatsResponse
from app.services import embedding_service
from app.database.mongodb import get_database
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/papers/{paper_id}/embeddings", response_model=EmbeddingStatsResponse)
def generate_paper_embeddings(
    paper_id: str,
    db: Database = Depends(get_database),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate embeddings for all valid chunks of a paper.
    """
    return embedding_service.generate_embeddings(db, paper_id, current_user["_id"])
