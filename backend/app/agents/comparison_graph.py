import json
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import logging

from app.services.llm_service import llm_service
from app.services.vector_service import vector_store
from app.services.citation_service import CitationManager

logger = logging.getLogger(__name__)

class ComparisonState(TypedDict):
    user_id: str
    project_id: str
    paper_ids: List[str]
    dimensions: List[str]
    query: Optional[str]
    
    # Populated during graph
    citation_manager: Any  # CitationManager instance
    retrieved_evidence: List[Dict[str, Any]]
    grouped_evidence: Dict[str, Dict[str, List[Dict[str, Any]]]]
    dimension_comparisons: List[Dict[str, Any]]
    overall_analysis: str
    
    # Outputs
    final_result: Optional[Dict[str, Any]]
    errors: List[str]

async def parse_comparison_request(state: ComparisonState) -> ComparisonState:
    if not state.get("dimensions") and not state.get("query"):
        state["dimensions"] = ["Methodology", "Results", "Limitations"]
        return state
        
    if state.get("query") and not state.get("dimensions"):
        # Use LLM to extract dimensions from query
        prompt = f"Extract a list of comparison dimensions from this query. Return ONLY a JSON list of strings.\nQuery: {state['query']}"
        messages = [{"role": "user", "content": prompt}]
        try:
            resp, _ = await llm_service.generate(messages)
            # basic cleanup
            resp = resp.strip().replace("```json", "").replace("```", "")
            dims = json.loads(resp)
            if isinstance(dims, list):
                state["dimensions"] = dims
        except Exception as e:
            logger.error(f"Failed to parse dimensions: {e}")
            state["dimensions"] = ["Methodology", "Results"]
            
    return state

async def validate_papers(state: ComparisonState) -> ComparisonState:
    if len(state["paper_ids"]) < 2:
        state["errors"].append("At least two papers must be provided.")
    if len(set(state["paper_ids"])) != len(state["paper_ids"]):
        state["errors"].append("Duplicate paper IDs provided.")
    return state

async def retrieve_paper_evidence(state: ComparisonState) -> ComparisonState:
    if state.get("errors"):
        return state
        
    all_chunks = []
    
    for paper_id in state["paper_ids"]:
        for dim in state["dimensions"]:
            # Retrieve specifically for this paper and dimension
            query = f"{dim} {state['query'] or ''}"
            # Need embedding
            from app.services.embedding_service import embedding_service
            query_embedding = embedding_service.generate_embeddings([query])[0]
            
            chunks = await vector_store.search(
                query_embedding=query_embedding,
                top_k=5,
                user_id=state["user_id"],
                paper_ids=[paper_id]
            )
            
            for c in chunks:
                c["matched_dimension"] = dim
                all_chunks.append(c)
                
    state["retrieved_evidence"] = all_chunks
    return state

async def group_evidence(state: ComparisonState) -> ComparisonState:
    if state.get("errors"):
        return state
        
    grouped = {pid: {dim: [] for dim in state["dimensions"]} for pid in state["paper_ids"]}
    
    for chunk in state["retrieved_evidence"]:
        pid = chunk["paper_id"]
        dim = chunk["matched_dimension"]
        if pid in grouped and dim in grouped[pid]:
            grouped[pid][dim].append(chunk)
            
    state["grouped_evidence"] = grouped
    return state

async def compare_evidence(state: ComparisonState) -> ComparisonState:
    if state.get("errors"):
        return state
        
    cm: CitationManager = state["citation_manager"]
    dim_comparisons = []
    
    for dim in state["dimensions"]:
        dim_comp = {
            "dimension": dim,
            "papers": [],
            "similarities": [],
            "differences": [],
            "analysis": ""
        }
        
        # Format chunks for LLM for this dimension
        context_parts = []
        for pid in state["paper_ids"]:
            chunks = state["grouped_evidence"][pid][dim]
            if not chunks:
                dim_comp["papers"].append({
                    "paper_id": pid,
                    "summary": f"No evidence found for {dim}.",
                    "citations": []
                })
                continue
                
            formatted = cm.register_chunks(chunks)
            context = cm.format_for_llm(formatted)
            context_parts.append(f"PAPER: {pid}\nEVIDENCE:\n{context}")
            
        full_context = "\n\n".join(context_parts)
        
        prompt = f"""Compare the papers based on the dimension: '{dim}'.
Use ONLY the provided evidence. Do not invent information.
If evidence is missing for a paper, state that.
For all factual claims, append the inline citation ID, e.g. [1].

EVIDENCE:
{full_context}

Return a JSON object with this exact schema:
{{
    "papers": [
        {{"paper_id": "...", "summary": "..."}}
    ],
    "similarities": ["..."],
    "differences": ["..."],
    "analysis": "..."
}}
"""
        try:
            resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
            resp = resp.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(resp)
            parsed["dimension"] = dim
            dim_comparisons.append(parsed)
        except Exception as e:
            logger.error(f"Error comparing dimension {dim}: {e}")
            dim_comparisons.append(dim_comp)
            
    state["dimension_comparisons"] = dim_comparisons
    return state

async def generate_overall_analysis(state: ComparisonState) -> ComparisonState:
    if state.get("errors"):
        return state
        
    summary_parts = []
    for dc in state["dimension_comparisons"]:
        summary_parts.append(f"Dimension: {dc['dimension']}\nAnalysis: {dc.get('analysis', '')}")
        
    prompt = "Based on the following dimensional analyses, provide a brief overall conclusion of the comparison.\n" + "\n\n".join(summary_parts)
    
    try:
        resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
        state["overall_analysis"] = resp
    except Exception as e:
        logger.error(f"Error generating overall analysis: {e}")
        state["overall_analysis"] = "Failed to generate overall analysis."
        
    return state

async def verify_citations(state: ComparisonState) -> ComparisonState:
    if state.get("errors"):
        return state
        
    cm: CitationManager = state["citation_manager"]
    
    # Verify citations in each dimension comparison
    for dc in state["dimension_comparisons"]:
        # Verify paper summaries
        for p in dc.get("papers", []):
            if "summary" in p:
                cleaned, sources = cm.validate_citations(p["summary"])
                p["summary"] = cleaned
                p["citations"] = sources
                
        # Verify analysis
        if "analysis" in dc:
            cleaned, sources = cm.validate_citations(dc["analysis"])
            dc["analysis"] = cleaned
            dc["citations"] = sources
            
        # Verify similarities/differences
        for i in range(len(dc.get("similarities", []))):
            cleaned, _ = cm.validate_citations(dc["similarities"][i])
            dc["similarities"][i] = cleaned
            
        for i in range(len(dc.get("differences", []))):
            cleaned, _ = cm.validate_citations(dc["differences"][i])
            dc["differences"][i] = cleaned
            
    return state

async def format_response(state: ComparisonState) -> ComparisonState:
    if state.get("errors"):
        return state
        
    state["final_result"] = {
        "comparisons": state["dimension_comparisons"],
        "overall_analysis": state["overall_analysis"],
        "limitations": []
    }
    return state

def should_continue(state: ComparisonState) -> str:
    if state.get("errors"):
        return END
    return "retrieve_paper_evidence"

# Build graph
workflow = StateGraph(ComparisonState)

workflow.add_node("parse_comparison_request", parse_comparison_request)
workflow.add_node("validate_papers", validate_papers)
workflow.add_node("retrieve_paper_evidence", retrieve_paper_evidence)
workflow.add_node("group_evidence", group_evidence)
workflow.add_node("compare_evidence", compare_evidence)
workflow.add_node("generate_overall_analysis", generate_overall_analysis)
workflow.add_node("verify_citations", verify_citations)
workflow.add_node("format_response", format_response)

workflow.set_entry_point("parse_comparison_request")
workflow.add_edge("parse_comparison_request", "validate_papers")
workflow.add_conditional_edges("validate_papers", should_continue)
workflow.add_edge("retrieve_paper_evidence", "group_evidence")
workflow.add_edge("group_evidence", "compare_evidence")
workflow.add_edge("compare_evidence", "generate_overall_analysis")
workflow.add_edge("generate_overall_analysis", "verify_citations")
workflow.add_edge("verify_citations", "format_response")
workflow.add_edge("format_response", END)

comparison_graph = workflow.compile()
