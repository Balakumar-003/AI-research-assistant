from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.research_question_graph import research_question_graph, ResearchQuestionState
from app.models.research_question_model import create_research_question_document
from app.schemas.research_question_schemas import ResearchQuestionRequest

class ResearchQuestionService:
    @staticmethod
    async def run_generation(db: Database, user_id: str, request: ResearchQuestionRequest) -> dict:
        from app.services.paper_service import validate_object_id
        
        project_obj_id = validate_object_id(request.project_id)
        
        # Verify project
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        initial_state: ResearchQuestionState = {
            "user_id": user_id,
            "project_id": request.project_id,
            "gap_ids": request.gap_ids,
            "topic": request.topic,
            "research_gaps": [],
            "literature_context": {},
            "candidate_questions": [],
            "final_questions": [],
            "errors": []
        }
        
        final_state = await research_question_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        final_questions = final_state.get("final_questions")
        
        if not final_questions:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate research questions.")
            
        doc = create_research_question_document(
            user_id=user_id,
            project_id=request.project_id,
            gap_ids=request.gap_ids,
            topic=request.topic,
            research_questions=final_questions,
            status="completed"
        )
        
        insert_res = db.research_questions.insert_one(doc)
        doc["_id"] = str(insert_res.inserted_id)
        return doc

    @staticmethod
    def get_generation(db: Database, user_id: str, question_set_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(question_set_id)
        
        doc = db.research_questions.find_one({"_id": obj_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research questions not found")
            
        doc["_id"] = str(doc["_id"])
        return doc
        
    @staticmethod
    def get_project_generations(db: Database, user_id: str, project_id: str) -> list:
        from app.services.paper_service import validate_object_id
        proj_obj_id = validate_object_id(project_id)
        
        docs = db.research_questions.find({"project_id": project_id, "user_id": user_id}).sort("created_at", -1)
        result = []
        for r in docs:
            result.append({
                "id": str(r["_id"]),
                "project_id": r["project_id"],
                "topic": r.get("topic"),
                "question_count": len(r.get("research_questions", [])),
                "status": r.get("status", "completed"),
                "created_at": r["created_at"]
            })
        return result

    @staticmethod
    def select_primary_question(db: Database, user_id: str, question_set_id: str, question_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(question_set_id)
        
        doc = db.research_questions.find_one({"_id": obj_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research questions not found")
            
        updated_questions = []
        for q in doc.get("research_questions", []):
            q["is_primary"] = (q["id"] == question_id)
            updated_questions.append(q)
            
        db.research_questions.update_one(
            {"_id": obj_id},
            {"$set": {"research_questions": updated_questions}}
        )
        
        doc["research_questions"] = updated_questions
        doc["_id"] = str(doc["_id"])
        return doc

research_question_service = ResearchQuestionService()
