from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResearchGoalCreate(BaseModel):
    project_id: str = Field(..., description="The ID of the project/workspace")
    topic: str
    objective: str
    problem_statement: Optional[str] = ""

class NextBestActionResponse(BaseModel):
    action_type: str
    description: str
    reason: str
    requires_approval: bool

class ResearchGoalResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    topic: str
    objective: str
    problem_statement: str
    status: str
    autonomy_level: int
    landscape: Dict[str, Any]
    knowledge_gaps: List[Dict[str, Any]]
    candidate_questions: List[Dict[str, Any]]
    candidate_methods: List[Dict[str, Any]]
    candidate_experiments: List[Dict[str, Any]]
    roadmap: List[Dict[str, Any]]
    next_best_actions: List[NextBestActionResponse]
    created_at: datetime
    updated_at: datetime
