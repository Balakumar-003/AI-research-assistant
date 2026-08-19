from datetime import datetime
from typing import Dict, Any, List, Optional

def create_chat_document(
    user_id: str,
    project_id: Optional[str],
    question: str,
    answer: str,
    citations: List[Dict[str, Any]],
    usage: Dict[str, int]
) -> Dict[str, Any]:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "question": question,
        "answer": answer,
        "citations": citations,
        "usage": usage,
        "created_at": now
    }
