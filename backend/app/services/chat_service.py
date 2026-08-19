from pymongo.database import Database
from typing import List, Dict, Any, Optional
from app.models.chat import create_chat_document

def save_turn(
    db: Database,
    user_id: str,
    project_id: Optional[str],
    question: str,
    answer: str,
    citations: List[Dict[str, Any]],
    usage: Dict[str, int]
):
    doc = create_chat_document(user_id, project_id, question, answer, citations, usage)
    db.chats.insert_one(doc)

def get_recent_history(
    db: Database,
    user_id: str,
    project_id: Optional[str],
    limit: int = 5
) -> List[Dict[str, Any]]:
    
    query = {"user_id": user_id}
    if project_id:
        query["project_id"] = project_id
        
    cursor = db.chats.find(query).sort("created_at", -1).limit(limit)
    
    # Needs to be chronologically ordered for prompt (oldest first)
    history = list(cursor)
    history.reverse()
    
    return history
