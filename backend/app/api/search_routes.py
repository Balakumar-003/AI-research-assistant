from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.schemas.vector_metadata import SearchRequest, SearchResponse, SearchResultItem
from app.services.vector_service import vector_store
from app.providers.embedding_provider import embedding_provider
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
async def search_vectors(
    request: SearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search chunks across all papers or a specific paper using FAISS.
    """
    # Embed the query
    query_embedding = embedding_provider.embed_query(request.query)
    
    # Search the vector store
    results = await vector_store.search(
        query_embedding=query_embedding,
        top_k=request.top_k,
        user_id=str(current_user["_id"]),
        paper_id=request.paper_id
    )
    
    # Format the response
    items = []
    for r in results:
        items.append(SearchResultItem(**r))
        
    return SearchResponse(
        results=items,
        total_found=len(items)
    )

@router.get("/search/stats")
async def get_vector_stats():
    """
    Admin/debug endpoint to get vector store statistics.
    """
    return vector_store.get_stats()
