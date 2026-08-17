from datetime import datetime
from typing import Dict, Any

def create_paper_document(filename: str, file_path: str, project_id: str, user_id: str) -> Dict[str, Any]:
    """
    Creates a new paper document formatted for MongoDB.
    """
    now = datetime.utcnow()
    return {
        "filename": filename,
        "file_path": file_path,
        "project_id": project_id,
        "user_id": user_id,
        "status": "uploaded",
        "page_count": None,
        "chunking_status": "not_started",
        "chunk_count": 0,
        "uploaded_at": now
    }
