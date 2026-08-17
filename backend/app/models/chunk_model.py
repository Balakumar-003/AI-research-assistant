from datetime import datetime
from typing import Dict, Any

def create_chunk_document(paper_id: str, project_id: str, user_id: str, chunk_index: int, text: str, page_start: int, page_end: int) -> Dict[str, Any]:
    """
    Creates a new document chunk formatted for MongoDB.
    """
    now = datetime.utcnow()
    return {
        "paper_id": paper_id,
        "project_id": project_id,
        "user_id": user_id,
        "chunk_index": chunk_index,
        "text": text,
        "page_start": page_start,
        "page_end": page_end,
        "created_at": now,
        "updated_at": now
    }
