from datetime import datetime
from typing import Dict, Any

def create_user_document(name: str, email: str, hashed_password: str, role: str = "user") -> Dict[str, Any]:
    """
    Creates a new user document formatted for MongoDB.
    """
    now = datetime.utcnow()
    return {
        "name": name,
        "email": email,
        "password": hashed_password,
        "is_active": True,
        "role": role,
        "created_at": now,
        "updated_at": now
    }
