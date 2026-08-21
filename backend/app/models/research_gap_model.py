from datetime import datetime
from typing import List, Optional

def create_research_gap_document(
    user_id: str,
    project_id: str,
    query: str,
    literature_review_id: Optional[str],
    paper_ids: List[str],
    candidate_gaps: List[dict],
    validated_gaps: List[dict],
    rejected_gaps: List[dict],
    result: dict,
    status: str = "completed"
) -> dict:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "query": query,
        "literature_review_id": literature_review_id,
        "paper_ids": paper_ids,
        "candidate_gaps": candidate_gaps,
        "validated_gaps": validated_gaps,
        "rejected_gaps": rejected_gaps,
        "result": result,
        "status": status,
        "created_at": now,
        "updated_at": now
    }
