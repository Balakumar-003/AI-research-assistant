from datetime import datetime
from typing import Dict, Any, List

def create_embedding_document(
    chunk_id: str,
    paper_id: str,
    project_id: str,
    user_id: str,
    chunk_index: int,
    embedding: List[float],
    embedding_model: str,
    embedding_dimension: int,
    page_start: int,
    page_end: int,
    status: str = "completed"
) -> Dict[str, Any]:
    """
    Creates a new embedding document formatted for MongoDB.
    """
    now = datetime.utcnow()
    return {
        "chunk_id": chunk_id,
        "paper_id": paper_id,
        "project_id": project_id,
        "user_id": user_id,
        "chunk_index": chunk_index,
        "embedding": embedding,
        "embedding_model": embedding_model,
        "embedding_dimension": embedding_dimension,
        "page_start": page_start,
        "page_end": page_end,
        "status": status,
        "created_at": now,
        "updated_at": now
    }
