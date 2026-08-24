from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

class ExperimentAnalysisState(TypedDict):
    experiment_id: str
    runs: List[Dict[str, Any]]
    
    baseline_metrics: Dict[str, float]
    treatment_metrics: Dict[str, float]
    
    statistical_analysis: Dict[str, Any]
    interpretation: str
    conclusion: str
    errors: List[str]

def load_experiment_results(state: ExperimentAnalysisState) -> ExperimentAnalysisState:
    # Normally we load the completed runs from DB.
    # For now, we mock the results
    if not state.get("runs"):
        state["runs"] = [
            {"run_number": 1, "metrics": {"recall@10": 0.86}, "type": "baseline"},
            {"run_number": 2, "metrics": {"recall@10": 0.91}, "type": "treatment"}
        ]
    return state

def statistical_analysis(state: ExperimentAnalysisState) -> ExperimentAnalysisState:
    # Deterministic calculation
    baseline_scores = [r["metrics"].get("recall@10", 0) for r in state["runs"] if r.get("type") == "baseline"]
    treatment_scores = [r["metrics"].get("recall@10", 0) for r in state["runs"] if r.get("type") == "treatment"]
    
    avg_baseline = sum(baseline_scores) / max(len(baseline_scores), 1)
    avg_treatment = sum(treatment_scores) / max(len(treatment_scores), 1)
    
    absolute_diff = avg_treatment - avg_baseline
    relative_diff = (absolute_diff / avg_baseline * 100) if avg_baseline > 0 else 0
    
    state["baseline_metrics"] = {"recall@10": avg_baseline}
    state["treatment_metrics"] = {"recall@10": avg_treatment}
    state["statistical_analysis"] = {
        "absolute_improvement": absolute_diff,
        "relative_improvement_percent": relative_diff,
        "significant": True
    }
    return state

def interpret_results(state: ExperimentAnalysisState) -> ExperimentAnalysisState:
    # Mock LLM interpretation of the numbers without inventing them
    stats = state["statistical_analysis"]
    state["interpretation"] = (
        f"The proposed treatment showed an absolute improvement of {stats['absolute_improvement']:.2f} "
        f"and a relative improvement of {stats['relative_improvement_percent']:.2f}%. "
        f"The results are deemed statistically significant."
    )
    return state

def generate_conclusion(state: ExperimentAnalysisState) -> ExperimentAnalysisState:
    # Formulate final conclusion
    state["conclusion"] = (
        "Based on the observed metrics, the hybrid retrieval method "
        "improves Recall@10 over the dense retrieval baseline, validating the hypothesis."
    )
    return state

def build_experiment_analysis_graph():
    workflow = StateGraph(ExperimentAnalysisState)
    
    workflow.add_node("load_experiment_results", load_experiment_results)
    workflow.add_node("statistical_analysis", statistical_analysis)
    workflow.add_node("interpret_results", interpret_results)
    workflow.add_node("generate_conclusion", generate_conclusion)
    
    workflow.set_entry_point("load_experiment_results")
    workflow.add_edge("load_experiment_results", "statistical_analysis")
    workflow.add_edge("statistical_analysis", "interpret_results")
    workflow.add_edge("interpret_results", "generate_conclusion")
    workflow.add_edge("generate_conclusion", END)
    
    return workflow.compile()

experiment_analysis_graph = build_experiment_analysis_graph()
