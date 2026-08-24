from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

class ReportGenerationState(TypedDict):
    report_id: str
    proposal_id: str
    action: str # "outline" or "section"
    section_name: Optional[str]
    
    context: Dict[str, Any]
    generated_content: Any # list for outline, str for section
    citations: List[Dict[str, Any]]
    errors: List[str]

def gather_context(state: ReportGenerationState) -> ReportGenerationState:
    # Mock gathering context from proposal, experiments, and literature
    state["context"] = {
        "proposal_summary": "Mock proposal summary",
        "experiment_metrics": {"recall@10": 0.91}
    }
    return state

def generate_outline(state: ReportGenerationState) -> ReportGenerationState:
    state["generated_content"] = [
        "Title",
        "1. Abstract",
        "2. Introduction",
        "3. Related Work",
        "4. Methodology",
        "5. Experimental Setup",
        "6. Results",
        "7. Discussion",
        "8. Conclusion",
        "9. References"
    ]
    return state

def generate_section(state: ReportGenerationState) -> ReportGenerationState:
    section = state.get("section_name", "")
    
    if section.lower() == "results":
        # Strictly use metrics from context
        metrics = state["context"].get("experiment_metrics", {})
        content = f"The proposed method achieved a Recall@10 of {metrics.get('recall@10', 'N/A')}."
    else:
        content = f"This is the AI-generated content for the {section} section, grounded in the context."
        
    state["generated_content"] = content
    state["citations"] = [{"id": "mock_cite", "source": "Literature"}]
    return state

def validate_content(state: ReportGenerationState) -> ReportGenerationState:
    # Ensure no hallucinations in the results section
    if state.get("action") == "section" and state.get("section_name", "").lower() == "results":
        if "0.91" not in state["generated_content"]:
            state["errors"].append("Failed to ground results accurately.")
    return state

def build_report_generation_graph():
    workflow = StateGraph(ReportGenerationState)
    
    workflow.add_node("gather_context", gather_context)
    workflow.add_node("generate_outline", generate_outline)
    workflow.add_node("generate_section", generate_section)
    workflow.add_node("validate_content", validate_content)
    
    # Conditional routing
    def route_action(state: ReportGenerationState) -> str:
        if state["action"] == "outline":
            return "generate_outline"
        return "generate_section"
        
    workflow.set_entry_point("gather_context")
    workflow.add_conditional_edges("gather_context", route_action, {
        "generate_outline": "generate_outline",
        "generate_section": "generate_section"
    })
    
    workflow.add_edge("generate_outline", END)
    workflow.add_edge("generate_section", "validate_content")
    workflow.add_edge("validate_content", END)
    
    return workflow.compile()

report_generation_graph = build_report_generation_graph()
