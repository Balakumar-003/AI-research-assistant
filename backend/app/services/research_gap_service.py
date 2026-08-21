from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.research_gap_graph import research_gap_graph, ResearchGapState
from app.services.citation_service import CitationManager
from app.models.research_gap_model import create_research_gap_document
from app.schemas.research_gap_schemas import ResearchGapRequest
from app.schemas.literature_review_schemas import LiteratureReviewRequest
from app.services.literature_review_service import literature_review_service

class ResearchGapService:
    @staticmethod
    async def run_discovery(db: Database, user_id: str, request: ResearchGapRequest) -> dict:
        from app.services.paper_service import validate_object_id
        
        project_obj_id = validate_object_id(request.project_id)
        
        # Verify project
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        literature_review_data = None
        paper_ids = []
        
        if request.literature_review_id:
            # Mode A: Load existing
            try:
                lr = literature_review_service.get_review(db, user_id, request.literature_review_id)
                literature_review_data = lr.get("result", {})
                paper_ids = lr.get("relevant_paper_ids", [])
            except Exception:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Literature review not found")
        else:
            # Mode B: Generate implicitly
            lr_req = LiteratureReviewRequest(
                project_id=request.project_id,
                query=request.query,
                paper_ids=[],
                max_papers=10
            )
            lr_doc = await literature_review_service.run_review(db, user_id, lr_req)
            literature_review_data = lr_doc.get("result", {})
            paper_ids = lr_doc.get("relevant_paper_ids", [])
            request.literature_review_id = lr_doc.get("_id")
            
        cm = CitationManager()
        
        initial_state: ResearchGapState = {
            "user_id": user_id,
            "project_id": request.project_id,
            "query": request.query,
            "literature_review_id": request.literature_review_id,
            "literature_review_data": literature_review_data,
            "citation_manager": cm,
            "literature_knowledge": {},
            "candidate_gaps": [],
            "validated_gaps": [],
            "rejected_gaps": [],
            "final_report": None,
            "errors": []
        }
        
        final_state = await research_gap_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        final_report = final_state.get("final_report")
        
        if not final_report:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate research gaps.")
            
        doc = create_research_gap_document(
            user_id=user_id,
            project_id=request.project_id,
            query=request.query,
            literature_review_id=request.literature_review_id,
            paper_ids=paper_ids,
            candidate_gaps=final_state.get("candidate_gaps", []),
            validated_gaps=final_state.get("validated_gaps", []),
            rejected_gaps=final_state.get("rejected_gaps", []),
            result=final_report,
            status="completed"
        )
        
        insert_res = db.research_gaps.insert_one(doc)
        doc["_id"] = str(insert_res.inserted_id)
        return doc

    @staticmethod
    def get_analysis(db: Database, user_id: str, analysis_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        gap_obj_id = validate_object_id(analysis_id)
        
        gap = db.research_gaps.find_one({"_id": gap_obj_id, "user_id": user_id})
        if not gap:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research gap analysis not found")
            
        gap["_id"] = str(gap["_id"])
        return gap
        
    @staticmethod
    def get_project_analyses(db: Database, user_id: str, project_id: str) -> list:
        from app.services.paper_service import validate_object_id
        proj_obj_id = validate_object_id(project_id)
        
        gaps = db.research_gaps.find({"project_id": project_id, "user_id": user_id}).sort("created_at", -1)
        result = []
        for r in gaps:
            result.append({
                "id": str(r["_id"]),
                "project_id": r["project_id"],
                "query": r["query"],
                "gap_count": len(r.get("validated_gaps", [])),
                "status": r.get("status", "completed"),
                "created_at": r["created_at"]
            })
        return result

research_gap_service = ResearchGapService()
