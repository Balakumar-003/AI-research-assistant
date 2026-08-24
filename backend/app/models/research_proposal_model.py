from datetime import datetime
from typing import List, Optional, Dict, Any

def create_research_proposal_document(
    user_id: str,
    project_id: str,
    research_question_id: str,
    research_gap_id: str,
    proposal_data: Dict[str, Any],
    status: str = "completed"
) -> dict:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "research_question_id": research_question_id,
        "research_gap_id": research_gap_id,
        "proposal": proposal_data,
        "status": status,
        "created_at": now,
        "updated_at": now
    }
