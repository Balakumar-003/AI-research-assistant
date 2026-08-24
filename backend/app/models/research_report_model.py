from datetime import datetime
from typing import List, Optional, Dict, Any

def create_research_report_document(
    user_id: str,
    project_id: str,
    proposal_id: str,
    title: str = "Untitled Research Paper",
    document_type: str = "Research Paper",
    status: str = "draft"
) -> dict:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "proposal_id": proposal_id,
        "title": title,
        "document_type": document_type,
        "abstract": "",
        "status": status,
        "version": 1,
        "outline": [],
        "sections": {},
        "citations": [],
        "created_at": now,
        "updated_at": now,
        "published_at": None
    }
