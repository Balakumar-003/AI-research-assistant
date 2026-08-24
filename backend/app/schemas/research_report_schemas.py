from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ReportCreateRequest(BaseModel):
    project_id: str = Field(..., description="The ID of the project")
    proposal_id: str = Field(..., description="The ID of the research proposal")
    title: str = "Untitled Research Paper"
    document_type: str = "Research Paper"

class OutlineGenerateRequest(BaseModel):
    pass # Can be expanded with preferences

class SectionGenerateRequest(BaseModel):
    section_name: str
    instructions: Optional[str] = None

class SectionUpdateRequest(BaseModel):
    content: str

class ResearchReportResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    proposal_id: str
    title: str
    document_type: str
    abstract: str
    status: str
    version: int
    outline: List[str]
    sections: Dict[str, str]
    citations: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
