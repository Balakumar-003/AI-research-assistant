import json
import logging
from typing import List, Dict, Any, Optional

from langchain_core.tools import tool
from app.providers.embedding_provider import embedding_provider
from app.services.vector_service import vector_store
from app.database.mongodb import get_database

logger = logging.getLogger(__name__)

# To make tools aware of user context, we will inject these variables globally per request 
# or use a ThreadLocal/ContextVar. For simplicity in LangGraph, we can pass them in the state 
# and have wrapper tools, or we assume the LLM generates arguments and we validate inside the tool.
# Langchain tools can accept run_manager which has metadata, but to keep it simple, 
# we'll inject user_id via a context variable.
import contextvars
from app.services.citation_service import CitationManager

user_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar('user_id', default="")
citation_manager_ctx: contextvars.ContextVar[CitationManager] = contextvars.ContextVar('citation_manager')

@tool
async def search_paper(query: str, paper_id: str, top_k: int = 5) -> str:
    """
    Search a specific research paper for relevant information.
    Use this tool when you need to extract methodology, results, or specific details from a single paper.
    
    Args:
        query: The semantic search query.
        paper_id: The ID of the paper to search.
        top_k: Number of chunks to retrieve.
    """
    user_id = user_id_ctx.get()
    
    logger.info(f"Tool search_paper called with query: {query}, paper_id: {paper_id}")
    query_embedding = embedding_provider.embed_query(query)
    
    chunks = await vector_store.search(
        query_embedding=query_embedding,
        top_k=top_k,
        user_id=user_id,
        paper_id=paper_id
    )
    
    if not chunks:
        return json.dumps({"success": True, "results": [], "message": "No relevant information was found."})
        
    cm = citation_manager_ctx.get()
    formatted_chunks = cm.register_chunks(chunks)
    context_text = cm.format_for_llm(formatted_chunks)
        
    return json.dumps({"success": True, "results": context_text})


@tool
async def search_multiple_papers(query: str, paper_ids: List[str], top_k: int = 5) -> str:
    """
    Search across multiple research papers simultaneously for relevant information.
    Use this tool when you need to compare methodologies, datasets, or results across multiple papers.
    
    Args:
        query: The semantic search query.
        paper_ids: A list of paper IDs to search across.
        top_k: Number of total chunks to retrieve.
    """
    user_id = user_id_ctx.get()
    
    logger.info(f"Tool search_multiple_papers called with query: {query}, paper_ids: {paper_ids}")
    query_embedding = embedding_provider.embed_query(query)
    
    chunks = await vector_store.search(
        query_embedding=query_embedding,
        top_k=top_k,
        user_id=user_id,
        paper_ids=paper_ids
    )
    
    if not chunks:
        return json.dumps({"success": True, "results": [], "message": "No relevant information was found."})
        
    cm = citation_manager_ctx.get()
    formatted_chunks = cm.register_chunks(chunks)
    context_text = cm.format_for_llm(formatted_chunks)
        
    return json.dumps({"success": True, "results": context_text})


@tool
def get_paper_metadata(paper_id: str) -> str:
    """
    Retrieve metadata for a specific paper.
    Use this tool to get the paper title, authors, publication date, or abstract.
    
    Args:
        paper_id: The ID of the paper.
    """
    user_id = user_id_ctx.get()
    logger.info(f"Tool get_paper_metadata called with paper_id: {paper_id}")
    
    # Resolve the db from dependency manually or use a new client
    # For now, we will create a quick connection just for metadata retrieval
    # In production, we'd pass it via dependencies, but langchain tools make it hard.
    from app.database.mongodb import get_db_client
    from app.core.config import settings
    from bson.objectid import ObjectId
    
    client = get_db_client()
    db = client[settings.MONGODB_DB_NAME]
    
    try:
        obj_id = ObjectId(paper_id)
        paper = db.papers.find_one({"_id": obj_id, "user_id": user_id})
        
        if not paper:
            return json.dumps({"success": False, "error": "Paper not found or unauthorized access."})
            
        metadata = {
            "title": paper.get("title"),
            "filename": paper.get("filename"),
            "uploaded_at": paper.get("uploaded_at").isoformat() if paper.get("uploaded_at") else None,
            "status": paper.get("status")
        }
        return json.dumps({"success": True, "metadata": metadata})
        
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


AGENT_TOOLS = [search_paper, search_multiple_papers, get_paper_metadata]
