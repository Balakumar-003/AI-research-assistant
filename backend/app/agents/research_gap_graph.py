import json
import logging
import uuid
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.services.llm_service import llm_service
from app.services.vector_service import vector_store
from app.providers.embedding_provider import embedding_provider
from app.services.citation_service import CitationManager
from app.core.config import settings

logger = logging.getLogger(__name__)

class ResearchGapState(TypedDict):
    user_id: str
    project_id: str
    query: str
    literature_review_id: Optional[str]
    literature_review_data: Optional[Dict[str, Any]]
    
    citation_manager: Any
    
    literature_knowledge: Dict[str, Any]
    candidate_gaps: List[Dict[str, Any]]
    validated_gaps: List[Dict[str, Any]]
    rejected_gaps: List[Dict[str, Any]]
    
    final_report: Optional[Dict[str, Any]]
    errors: List[str]

async def load_literature_review(state: ResearchGapState) -> ResearchGapState:
    # If literature_review_id is not provided, or data is not pre-populated, error out or handle.
    # In this implementation, we expect the service to pre-populate literature_review_data
    # either by fetching the review or running a lightweight analysis if Mode B.
    if not state.get("literature_review_data"):
        state["errors"].append("No literature review data available to base gap discovery on.")
    return state

async def extract_literature_knowledge(state: ResearchGapState) -> ResearchGapState:
    if state.get("errors"): return state
    
    data = state["literature_review_data"]
    
    # Just extract key parts
    state["literature_knowledge"] = {
        "themes": [t.get("name") for t in data.get("themes", [])],
        "findings": [f for t in data.get("themes", []) for f in t.get("findings", [])],
        "limitations": data.get("common_limitations", []),
        "contradictions": data.get("contradictory_findings", []),
        "emerging": data.get("emerging_directions", []),
    }
    return state

async def generate_candidate_gaps(state: ResearchGapState) -> ResearchGapState:
    if state.get("errors"): return state
    
    knowledge = state["literature_knowledge"]
    prompt = f"""Based on this literature knowledge for '{state["query"]}', brainstorm up to {settings.MAX_GAP_CANDIDATES} candidate research gaps.
    
    Themes: {knowledge['themes']}
    Findings: {knowledge['findings']}
    Limitations: {knowledge['limitations']}
    Contradictions: {knowledge['contradictions']}
    
    Return EXACTLY a JSON list of objects:
    [{{
       "title": "...",
       "statement": "...",
       "type": ["evaluation_gap", "dataset_gap", "methodological_gap", "etc"]
    }}]
    """
    
    try:
        resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
        resp = resp.strip().replace("```json", "").replace("```", "")
        candidates = json.loads(resp)
        for c in candidates:
            c["gap_id"] = str(uuid.uuid4())
            c["supporting_evidence"] = []
            c["counter_evidence"] = []
        state["candidate_gaps"] = candidates[:settings.MAX_GAP_CANDIDATES]
    except Exception as e:
        logger.error(f"Error generating candidates: {e}")
        state["candidate_gaps"] = []
        
    return state

async def retrieve_evidence(state: ResearchGapState) -> ResearchGapState:
    if state.get("errors"): return state
    
    # Retrieve evidence and counter-evidence using Vector Search
    for gap in state["candidate_gaps"]:
        gap_stmt = gap["statement"]
        
        # Supporting evidence query
        sup_query = f"Evidence supporting the limitation or gap: {gap_stmt}"
        sup_emb = embedding_provider.embed_query(sup_query)
        sup_chunks = await vector_store.search(
            query_embedding=sup_emb,
            top_k=settings.MAX_EVIDENCE_PER_GAP,
            user_id=state["user_id"]
        )
        gap["supporting_evidence"] = sup_chunks
        
        # Counter evidence query
        ctr_query = f"Evidence contradicting the limitation, showing this is ALREADY solved or researched: {gap_stmt}"
        ctr_emb = embedding_provider.embed_query(ctr_query)
        ctr_chunks = await vector_store.search(
            query_embedding=ctr_emb,
            top_k=settings.MAX_COUNTER_EVIDENCE,
            user_id=state["user_id"]
        )
        gap["counter_evidence"] = ctr_chunks
        
    return state

async def validate_gaps(state: ResearchGapState) -> ResearchGapState:
    if state.get("errors"): return state
    
    validated = []
    rejected = []
    cm: CitationManager = state["citation_manager"]
    
    for gap in state["candidate_gaps"]:
        sup = cm.format_for_llm(cm.register_chunks(gap["supporting_evidence"]))
        ctr = cm.format_for_llm(cm.register_chunks(gap["counter_evidence"]))
        
        prompt = f"""Evaluate this candidate research gap based ONLY on the provided evidence.
        
        Gap Statement: {gap['statement']}
        
        Supporting Evidence: {sup}
        
        Counter Evidence: {ctr}
        
        If the counter-evidence shows this is well-studied, reject it.
        If it's supported, validate and optionally refine the statement to be less absolute.
        Provide importance (HIGH/MEDIUM/LOW) and confidence (HIGH/MEDIUM/LOW).
        
        Return EXACTLY JSON:
        {{
            "status": "VALIDATED" or "REJECTED",
            "refined_statement": "...",
            "importance": "...",
            "confidence": "...",
            "evidence_summary": "...",
            "why_it_matters": "...",
            "potential_research_direction": "..."
        }}
        """
        
        try:
            resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
            resp = resp.strip().replace("```json", "").replace("```", "")
            eval_data = json.loads(resp)
            
            if eval_data.get("status") == "VALIDATED":
                gap["statement"] = eval_data.get("refined_statement", gap["statement"])
                gap["importance"] = eval_data.get("importance", "MEDIUM")
                gap["confidence"] = eval_data.get("confidence", "MEDIUM")
                gap["evidence_summary"] = eval_data.get("evidence_summary", "")
                gap["why_it_matters"] = eval_data.get("why_it_matters", "")
                gap["potential_research_direction"] = eval_data.get("potential_research_direction", "")
                
                # Deduplicate supporting papers
                sup_pids = list(set([c["paper_id"] for c in gap["supporting_evidence"]]))
                gap["supporting_papers"] = sup_pids
                gap["citations"] = []
                validated.append(gap)
            else:
                gap["rejection_reason"] = "Counter-evidence found or insufficient support."
                rejected.append(gap)
                
        except Exception as e:
            logger.error(f"Error validating gap: {e}")
            rejected.append(gap)
            
    state["validated_gaps"] = validated
    state["rejected_gaps"] = rejected
    
    if not validated:
        state["errors"].append("No sufficiently supported research gaps were identified from the available literature.")
        
    return state

async def generate_gap_report(state: ResearchGapState) -> ResearchGapState:
    if state.get("errors"): return state
    
    # Sort by confidence/importance conceptually
    val = state["validated_gaps"]
    
    def score(g):
        s = 0
        if g["confidence"] == "HIGH": s += 10
        if g["importance"] == "HIGH": s += 5
        return s
        
    val.sort(key=score, reverse=True)
    val = val[:settings.MAX_FINAL_GAPS]
    state["validated_gaps"] = val
    
    prompt = f"Write a 1-paragraph summary for the overall identified research gaps regarding: {state['query']}"
    try:
        overall, _ = await llm_service.generate([{"role": "user", "content": prompt}])
    except:
        overall = ""
        
    state["final_report"] = {
        "research_question": state["query"],
        "literature_scope": f"Based on review with {len(state['literature_review_data'].get('relevant_papers', []))} papers",
        "research_landscape": "Automated pipeline analysis.",
        "identified_gaps": val,
        "contradictory_findings": state["literature_knowledge"]["contradictions"],
        "overall_gap_summary": overall,
        "citations": state["citation_manager"].get_registry()
    }
    
    return state

def should_continue(state: ResearchGapState) -> str:
    if state.get("errors"):
        return END
    return "extract_literature_knowledge"

workflow = StateGraph(ResearchGapState)

workflow.add_node("load_literature_review", load_literature_review)
workflow.add_node("extract_literature_knowledge", extract_literature_knowledge)
workflow.add_node("generate_candidate_gaps", generate_candidate_gaps)
workflow.add_node("retrieve_evidence", retrieve_evidence)
workflow.add_node("validate_gaps", validate_gaps)
workflow.add_node("generate_gap_report", generate_gap_report)

workflow.set_entry_point("load_literature_review")
workflow.add_conditional_edges("load_literature_review", should_continue)
workflow.add_edge("extract_literature_knowledge", "generate_candidate_gaps")
workflow.add_edge("generate_candidate_gaps", "retrieve_evidence")
workflow.add_edge("retrieve_evidence", "validate_gaps")
workflow.add_edge("validate_gaps", "generate_gap_report")
workflow.add_edge("generate_gap_report", END)

research_gap_graph = workflow.compile()
