from datetime import datetime
from typing import Dict, Any

def create_project_document(name: str, description: str, user_id: str) -> Dict[str, Any]:
    """
    Creates a new project document formatted for MongoDB.
    """
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "name": name,
        "description": description,
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }
