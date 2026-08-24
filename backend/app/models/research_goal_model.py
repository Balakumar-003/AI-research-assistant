from datetime import datetime
from typing import List, Optional, Dict, Any

def create_research_goal_document(
    user_id: str,
    project_id: str,
    topic: str,
    objective: str,
    problem_statement: str = "",
    status: str = "draft"
) -> dict:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "topic": topic,
        "objective": objective,
        "problem_statement": problem_statement,
        "status": status,
        "autonomy_level": 1,
        "landscape": {},
        "knowledge_gaps": [],
        "candidate_questions": [],
        "candidate_methods": [],
        "candidate_experiments": [],
        "roadmap": [],
        "next_best_actions": [],
        "created_at": now,
        "updated_at": now
    }
