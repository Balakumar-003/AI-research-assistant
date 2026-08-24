from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from app.services.auth_service import get_current_user
from app.database.connection import get_db
from pymongo.database import Database
from app.schemas.research_report_schemas import (
    ReportCreateRequest,
    OutlineGenerateRequest,
    SectionGenerateRequest,
    SectionUpdateRequest,
    ResearchReportResponse
)
from app.services.report_generation_service import report_generation_service

router = APIRouter(prefix="/workspaces/{workspace_id}/reports", tags=["Reports"])

@router.post("", response_model=ResearchReportResponse)
def create_report(
    workspace_id: str,
    request: ReportCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    if request.project_id != workspace_id:
        request.project_id = workspace_id
    
    return report_generation_service.create_report(
        db=db,
        user_id=current_user["uid"],
        request=request
    )

@router.get("/{report_id}", response_model=ResearchReportResponse)
def get_report(
    workspace_id: str,
    report_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return report_generation_service.get_report(
        db=db,
        user_id=current_user["uid"],
        report_id=report_id
    )

@router.post("/{report_id}/outline", response_model=ResearchReportResponse)
async def generate_outline(
    workspace_id: str,
    report_id: str,
    request: OutlineGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return await report_generation_service.generate_outline(
        db=db,
        user_id=current_user["uid"],
        report_id=report_id,
        request=request
    )

@router.post("/{report_id}/sections", response_model=ResearchReportResponse)
async def generate_section(
    workspace_id: str,
    report_id: str,
    request: SectionGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return await report_generation_service.generate_section(
        db=db,
        user_id=current_user["uid"],
        report_id=report_id,
        request=request
    )

@router.patch("/{report_id}/sections/{section_name}", response_model=ResearchReportResponse)
def update_section(
    workspace_id: str,
    report_id: str,
    section_name: str,
    request: SectionUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return report_generation_service.update_section(
        db=db,
        user_id=current_user["uid"],
        report_id=report_id,
        section_name=section_name,
        request=request
    )
