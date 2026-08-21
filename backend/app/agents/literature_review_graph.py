import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.services.llm_service import llm_service
from app.services.vector_service import vector_store
from app.services.citation_service import CitationManager
from app.core.config import settings

logger = logging.getLogger(__name__)

class LiteratureReviewState(TypedDict):
    user_id: str
    project_id: str
    query: str
    paper_ids: List[str]
    max_papers: int
    
    citation_manager: Any
    
    # Scope and Relevance
    scope: str
    relevant_paper_ids: List[str]
    
    # Evidence & Insights
    retrieved_evidence: Dict[str, List[Dict[str, Any]]] # paper_id -> [chunks]
    paper_insights: Dict[str, str] # paper_id -> summary
    
    # Themes & Cross-paper
    themes: List[Dict[str, Any]] # {name, description, paper_ids, findings, agreements, disagreements, citations}
    trends: List[str]
    common_limitations: List[str]
    emerging_directions: List[str]
    overall_synthesis: str
    
    # Outputs
    final_result: Optional[Dict[str, Any]]
    errors: List[str]

async def parse_research_question(state: LiteratureReviewState) -> LiteratureReviewState:
    # Use LLM to extract scope and keywords
    prompt = f"Analyze this research question for a literature review: '{state['query']}'. Give a 1-sentence description of the research scope."
    try:
        resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
        state["scope"] = resp.strip()
    except Exception as e:
        logger.error(f"Error parsing question: {e}")
        state["scope"] = state["query"]
    return state

async def select_relevant_papers(state: LiteratureReviewState) -> LiteratureReviewState:
    # If paper_ids provided, filter those. Else, search all project papers.
    # We will do a generic vector search to find top papers.
    from app.providers.embedding_provider import embedding_provider
    query_emb = embedding_provider.embed_query(state["query"])
    
    chunks = await vector_store.search(
        query_embedding=query_emb,
        top_k=50,  # wide net
        user_id=state["user_id"]
    )
    
    paper_scores = {}
    for c in chunks:
        pid = c["paper_id"]
        if state["paper_ids"] and pid not in state["paper_ids"]:
            continue
        paper_scores[pid] = paper_scores.get(pid, 0) + c.get("score", 1.0)
        
    sorted_papers = sorted(paper_scores.items(), key=lambda x: x[1], reverse=True)
    top_papers = [p[0] for p in sorted_papers[:state["max_papers"]]]
    
    if not top_papers:
        if state["paper_ids"]:
            # Fallback if specific papers requested but scored low
            top_papers = state["paper_ids"][:state["max_papers"]]
        else:
            state["errors"].append("No sufficiently relevant papers were found in this research workspace for the requested topic.")
            
    state["relevant_paper_ids"] = top_papers
    return state

async def retrieve_evidence(state: LiteratureReviewState) -> LiteratureReviewState:
    if state.get("errors"):
        return state
        
    from app.providers.embedding_provider import embedding_provider
    query_emb = embedding_provider.embed_query(state["query"])
    
    retrieved = {}
    for pid in state["relevant_paper_ids"]:
        chunks = await vector_store.search(
            query_embedding=query_emb,
            top_k=settings.LITERATURE_REVIEW_TOP_K,
            user_id=state["user_id"],
            paper_ids=[pid]
        )
        retrieved[pid] = chunks
        
    state["retrieved_evidence"] = retrieved
    return state

async def extract_paper_insights(state: LiteratureReviewState) -> LiteratureReviewState:
    if state.get("errors"):
        return state
        
    cm: CitationManager = state["citation_manager"]
    insights = {}
    
    for pid, chunks in state["retrieved_evidence"].items():
        if not chunks:
            continue
            
        formatted_chunks = cm.register_chunks(chunks)
        context = cm.format_for_llm(formatted_chunks)
        
        prompt = f"""Extract insights for this research query from the provided evidence.
Query: {state['query']}
Evidence:
{context}

Summarize findings, methodologies, and limitations. Use inline citations [ID]."""
        
        try:
            resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
            insights[pid] = resp
        except Exception:
            insights[pid] = "Failed to extract insights."
            
    state["paper_insights"] = insights
    return state

async def discover_themes(state: LiteratureReviewState) -> LiteratureReviewState:
    if state.get("errors"):
        return state
        
    # Combine insights to discover themes
    cm = state["citation_manager"]
    combined = []
    for pid, text in state["paper_insights"].items():
        combined.append(f"PAPER {pid} INSIGHTS:\n{text}")
        
    full_context = "\n\n".join(combined)
    
    prompt = f"""Analyze the provided paper insights and extract major research themes, agreements, disagreements, trends, and limitations.
Query: {state['query']}

Insights:
{full_context}

Return EXACTLY a JSON object with this schema:
{{
  "themes": [
    {{
      "name": "Theme Name",
      "description": "...",
      "paper_ids": ["..."],
      "findings": ["..."],
      "agreements": ["..."],
      "disagreements": ["..."]
    }}
  ],
  "trends": ["..."],
  "common_limitations": ["..."],
  "emerging_directions": ["..."]
}}
"""
    try:
        resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
        resp = resp.strip().replace("```json", "").replace("```", "")
        parsed = json.loads(resp)
        state["themes"] = parsed.get("themes", [])
        for t in state["themes"]:
            t["citations"] = []
        state["trends"] = parsed.get("trends", [])
        state["common_limitations"] = parsed.get("common_limitations", [])
        state["emerging_directions"] = parsed.get("emerging_directions", [])
    except Exception as e:
        logger.error(f"Failed to discover themes: {e}")
        state["themes"] = []
        state["trends"] = []
        state["common_limitations"] = []
        state["emerging_directions"] = []
        
    return state

async def generate_overall_synthesis(state: LiteratureReviewState) -> LiteratureReviewState:
    if state.get("errors"):
        return state
        
    # generate overall synthesis
    prompt = f"Write a 2-paragraph overall synthesis for the literature review on: '{state['query']}' based on these themes: {[t['name'] for t in state['themes']]}"
    try:
        resp, _ = await llm_service.generate([{"role": "user", "content": prompt}])
        state["overall_synthesis"] = resp
    except:
        state["overall_synthesis"] = ""
        
    return state

async def verify_citations(state: LiteratureReviewState) -> LiteratureReviewState:
    if state.get("errors"):
        return state
        
    cm: CitationManager = state["citation_manager"]
    
    for theme in state["themes"]:
        for i in range(len(theme["findings"])):
            cleaned, _ = cm.validate_citations(theme["findings"][i])
            theme["findings"][i] = cleaned
        for i in range(len(theme["agreements"])):
            cleaned, _ = cm.validate_citations(theme["agreements"][i])
            theme["agreements"][i] = cleaned
        for i in range(len(theme["disagreements"])):
            cleaned, _ = cm.validate_citations(theme["disagreements"][i])
            theme["disagreements"][i] = cleaned
            
    for i in range(len(state["trends"])):
        cleaned, _ = cm.validate_citations(state["trends"][i])
        state["trends"][i] = cleaned
        
    for i in range(len(state["common_limitations"])):
        cleaned, _ = cm.validate_citations(state["common_limitations"][i])
        state["common_limitations"][i] = cleaned
        
    for i in range(len(state["emerging_directions"])):
        cleaned, _ = cm.validate_citations(state["emerging_directions"][i])
        state["emerging_directions"][i] = cleaned
        
    cleaned_synthesis, sources = cm.validate_citations(state["overall_synthesis"])
    state["overall_synthesis"] = cleaned_synthesis
    # we can store global citations in the final result later
    
    return state

async def quality_check(state: LiteratureReviewState) -> LiteratureReviewState:
    if state.get("errors"):
        return state
    # A simple stub for quality check
    return state

async def format_review(state: LiteratureReviewState) -> LiteratureReviewState:
    if state.get("errors"):
        return state
        
    state["final_result"] = {
        "research_question": state["query"],
        "scope": state["scope"],
        "relevant_papers": state["relevant_paper_ids"],
        "themes": state["themes"],
        "trends": state["trends"],
        "common_limitations": state["common_limitations"],
        "emerging_directions": state["emerging_directions"],
        "overall_synthesis": state["overall_synthesis"],
        "citations": state["citation_manager"].get_registry()
    }
    return state

def should_continue(state: LiteratureReviewState) -> str:
    if state.get("errors"):
        return END
    return "retrieve_evidence"

# Build Graph
workflow = StateGraph(LiteratureReviewState)

workflow.add_node("parse_research_question", parse_research_question)
workflow.add_node("select_relevant_papers", select_relevant_papers)
workflow.add_node("retrieve_evidence", retrieve_evidence)
workflow.add_node("extract_paper_insights", extract_paper_insights)
workflow.add_node("discover_themes", discover_themes)
workflow.add_node("generate_overall_synthesis", generate_overall_synthesis)
workflow.add_node("verify_citations", verify_citations)
workflow.add_node("quality_check", quality_check)
workflow.add_node("format_review", format_review)

workflow.set_entry_point("parse_research_question")
workflow.add_edge("parse_research_question", "select_relevant_papers")
workflow.add_conditional_edges("select_relevant_papers", should_continue)
workflow.add_edge("retrieve_evidence", "extract_paper_insights")
workflow.add_edge("extract_paper_insights", "discover_themes")
workflow.add_edge("discover_themes", "generate_overall_synthesis")
workflow.add_edge("generate_overall_synthesis", "verify_citations")
workflow.add_edge("verify_citations", "quality_check")
workflow.add_edge("quality_check", "format_review")
workflow.add_edge("format_review", END)

literature_review_graph = workflow.compile()
