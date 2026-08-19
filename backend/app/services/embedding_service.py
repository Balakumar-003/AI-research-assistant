import logging
from pymongo.database import Database
from fastapi import HTTPException, status
from bson.objectid import ObjectId
from typing import List, Dict, Any

from app.core.config import settings
from app.providers.embedding_provider import embedding_provider
from app.models.embedding_model import create_embedding_document

logger = logging.getLogger(__name__)

def generate_embeddings(db: Database, paper_id: str, user_id: str) -> Dict[str, Any]:
    """
    Generates and stores embeddings for all valid chunks of a paper.
    """
    # Verify paper exists and belongs to user
    paper = db.papers.find_one({"_id": ObjectId(paper_id), "user_id": user_id})
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found or unauthorized"
        )
    
    # Check if chunking was completed
    if paper.get("chunking_status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paper chunking is not completed yet"
        )
    
    # Check if embeddings already exist
    existing_count = db.embeddings.count_documents({"paper_id": paper_id})
    if existing_count > 0:
        return {
            "paper_id": paper_id,
            "status": "already_completed",
            "embedding_count": existing_count,
            "embedding_model": embedding_provider.model_name,
            "embedding_dimension": embedding_provider.dimension
        }

    # Fetch chunks
    chunks = list(db.chunks.find({"paper_id": paper_id}).sort("chunk_index", 1))
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No chunks found for this paper"
        )

    # Filter out empty chunks and prepare texts
    valid_chunks = [c for c in chunks if c.get("text") and c.get("text").strip()]
    if not valid_chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid text chunks found"
        )
    
    texts = [c["text"] for c in valid_chunks]
    
    logger.info(f"Generating embeddings for paper {paper_id}: {len(texts)} chunks")
    
    try:
        # Generate embeddings in batches using provider
        vectors = embedding_provider.embed_documents(texts)
        
        # Prepare embedding documents for MongoDB
        embedding_docs = []
        for i, chunk in enumerate(valid_chunks):
            doc = create_embedding_document(
                chunk_id=str(chunk["_id"]),
                paper_id=paper_id,
                project_id=chunk.get("project_id", ""),
                user_id=user_id,
                chunk_index=chunk["chunk_index"],
                embedding=vectors[i],
                embedding_model=embedding_provider.model_name,
                embedding_dimension=embedding_provider.dimension,
                page_start=chunk.get("page_start", 0),
                page_end=chunk.get("page_end", 0),
                status="completed"
            )
            embedding_docs.append(doc)
            
        # Store embeddings in DB
        db.embeddings.insert_many(embedding_docs)
        
        # Update paper status
        db.papers.update_one(
            {"_id": ObjectId(paper_id)},
            {"$set": {"embedding_status": "completed"}}
        )
        
        return {
            "paper_id": paper_id,
            "status": "completed",
            "embedding_count": len(embedding_docs),
            "embedding_model": embedding_provider.model_name,
            "embedding_dimension": embedding_provider.dimension
        }
        
    except Exception as e:
        logger.error(f"Error generating embeddings for paper {paper_id}: {str(e)}")
        # Update paper status to failed
        db.papers.update_one(
            {"_id": ObjectId(paper_id)},
            {"$set": {"embedding_status": "failed"}}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate embeddings: {str(e)}"
        )
