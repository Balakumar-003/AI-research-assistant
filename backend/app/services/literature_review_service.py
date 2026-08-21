from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.literature_review_graph import literature_review_graph, LiteratureReviewState
from app.services.citation_service import CitationManager
from app.models.literature_review_model import create_literature_review_document
from app.schemas.literature_review_schemas import LiteratureReviewRequest

class LiteratureReviewService:
    @staticmethod
    async def run_review(db: Database, user_id: str, request: LiteratureReviewRequest) -> dict:
        from app.services.paper_service import validate_object_id
        
        project_obj_id = validate_object_id(request.project_id)
        
        # Verify project
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        # Verify papers if provided
        for paper_id in request.paper_ids:
            paper_obj_id = validate_object_id(paper_id)
            paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id, "project_id": request.project_id})
            if not paper:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Paper {paper_id} not found in this project."
                )
                
        cm = CitationManager()
        
        initial_state: LiteratureReviewState = {
            "user_id": user_id,
            "project_id": request.project_id,
            "query": request.query,
            "paper_ids": request.paper_ids,
            "max_papers": request.max_papers,
            "citation_manager": cm,
            "scope": "",
            "relevant_paper_ids": [],
            "retrieved_evidence": {},
            "paper_insights": {},
            "themes": [],
            "trends": [],
            "common_limitations": [],
            "emerging_directions": [],
            "overall_synthesis": "",
            "final_result": None,
            "errors": []
        }
        
        final_state = await literature_review_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        final_result = final_state.get("final_result")
        
        if not final_result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate literature review.")
            
        doc = create_literature_review_document(
            user_id=user_id,
            project_id=request.project_id,
            query=request.query,
            paper_ids=request.paper_ids,
            relevant_paper_ids=final_state.get("relevant_paper_ids", []),
            result=final_result,
            status="completed"
        )
        
        insert_res = db.literature_reviews.insert_one(doc)
        doc["_id"] = str(insert_res.inserted_id)
        return doc

    @staticmethod
    def get_review(db: Database, user_id: str, review_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        rev_obj_id = validate_object_id(review_id)
        
        rev = db.literature_reviews.find_one({"_id": rev_obj_id, "user_id": user_id})
        if not rev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Literature review not found")
            
        rev["_id"] = str(rev["_id"])
        return rev
        
    @staticmethod
    def get_project_reviews(db: Database, user_id: str, project_id: str) -> list:
        from app.services.paper_service import validate_object_id
        proj_obj_id = validate_object_id(project_id)
        
        reviews = db.literature_reviews.find({"project_id": project_id, "user_id": user_id}).sort("created_at", -1)
        result = []
        for r in reviews:
            result.append({
                "id": str(r["_id"]),
                "project_id": r["project_id"],
                "query": r["query"],
                "paper_count": len(r.get("relevant_paper_ids", [])),
                "status": r.get("status", "completed"),
                "created_at": r["created_at"]
            })
        return result

literature_review_service = LiteratureReviewService()
