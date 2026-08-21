from datetime import datetime
from typing import List, Optional

def create_comparison_document(
    user_id: str,
    project_id: str,
    paper_ids: List[str],
    dimensions: List[str],
    query: Optional[str],
    result: dict
) -> dict:
    """
    Creates a new comparison document structure for MongoDB.
    """
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "paper_ids": paper_ids,
        "dimensions": dimensions,
        "query": query,
        "result": result,
        "created_at": now,
        "updated_at": now
    }
