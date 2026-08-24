from datetime import datetime
from typing import List, Optional, Dict, Any

def create_research_question_document(
    user_id: str,
    project_id: str,
    gap_ids: List[str],
    topic: Optional[str],
    research_questions: List[Dict[str, Any]],
    status: str = "completed"
) -> dict:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "gap_ids": gap_ids,
        "topic": topic,
        "research_questions": research_questions,
        "status": status,
        "created_at": now,
        "updated_at": now
    }
