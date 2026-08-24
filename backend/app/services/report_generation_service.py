from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.report_generation_graph import report_generation_graph, ReportGenerationState
from app.models.research_report_model import create_research_report_document
from app.schemas.research_report_schemas import ReportCreateRequest, OutlineGenerateRequest, SectionGenerateRequest, SectionUpdateRequest
from bson.objectid import ObjectId

class ReportGenerationService:
    @staticmethod
    def create_report(db: Database, user_id: str, request: ReportCreateRequest) -> dict:
        from app.services.paper_service import validate_object_id
        project_obj_id = validate_object_id(request.project_id)
        
        # Verify project
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        doc = create_research_report_document(
            user_id=user_id,
            project_id=request.project_id,
            proposal_id=request.proposal_id,
            title=request.title,
            document_type=request.document_type
        )
        
        insert_res = db.research_reports.insert_one(doc)
        doc["_id"] = str(insert_res.inserted_id)
        return doc

    @staticmethod
    def get_report(db: Database, user_id: str, report_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(report_id)
        
        doc = db.research_reports.find_one({"_id": obj_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research report not found")
            
        doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    async def generate_outline(db: Database, user_id: str, report_id: str, request: OutlineGenerateRequest) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(report_id)
        
        report = ReportGenerationService.get_report(db, user_id, report_id)
        
        initial_state: ReportGenerationState = {
            "report_id": report_id,
            "proposal_id": report["proposal_id"],
            "action": "outline",
            "section_name": None,
            "context": {},
            "generated_content": [],
            "citations": [],
            "errors": []
        }
        
        final_state = await report_generation_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        outline = final_state.get("generated_content", [])
        
        db.research_reports.update_one(
            {"_id": obj_id},
            {"$set": {"outline": outline}}
        )
        
        report["outline"] = outline
        return report

    @staticmethod
    async def generate_section(db: Database, user_id: str, report_id: str, request: SectionGenerateRequest) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(report_id)
        
        report = ReportGenerationService.get_report(db, user_id, report_id)
        
        initial_state: ReportGenerationState = {
            "report_id": report_id,
            "proposal_id": report["proposal_id"],
            "action": "section",
            "section_name": request.section_name,
            "context": {},
            "generated_content": "",
            "citations": [],
            "errors": []
        }
        
        final_state = await report_generation_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        content = final_state.get("generated_content", "")
        
        db.research_reports.update_one(
            {"_id": obj_id},
            {
                "$set": {f"sections.{request.section_name}": content},
                "$inc": {"version": 1}
            }
        )
        
        report["sections"][request.section_name] = content
        report["version"] += 1
        return report

    @staticmethod
    def update_section(db: Database, user_id: str, report_id: str, section_name: str, request: SectionUpdateRequest) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(report_id)
        
        report = ReportGenerationService.get_report(db, user_id, report_id)
        
        db.research_reports.update_one(
            {"_id": obj_id},
            {
                "$set": {f"sections.{section_name}": request.content},
                "$inc": {"version": 1}
            }
        )
        
        report["sections"][section_name] = request.content
        report["version"] += 1
        return report

report_generation_service = ReportGenerationService()
