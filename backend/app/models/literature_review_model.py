from datetime import datetime
from typing import List, Optional

def create_literature_review_document(
    user_id: str,
    project_id: str,
    query: str,
    paper_ids: List[str],
    relevant_paper_ids: List[str],
    result: dict,
    status: str = "completed"
) -> dict:
    """
    Creates a new literature review document structure for MongoDB.
    """
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "query": query,
        "paper_ids": paper_ids,
        "relevant_paper_ids": relevant_paper_ids,
        "result": result,
        "status": status,
        "created_at": now,
        "updated_at": now
    }
