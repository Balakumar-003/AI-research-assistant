import logging
from pymongo.database import Database
from app.core.config import settings
from app.rag.vector_store import VectorDBService

logger = logging.getLogger(__name__)

# Global instance
vector_store = VectorDBService(
    dim=settings.EMBEDDING_DIM,
    index_path=settings.VECTOR_STORE_PATH,
    metadata_path=settings.VECTOR_METADATA_PATH
)

async def add_paper_embeddings_to_faiss(db: Database, paper_id: str):
    """
    Fetches embeddings from MongoDB for a given paper and adds them to FAISS.
    """
    logger.info(f"Syncing embeddings for paper {paper_id} to FAISS...")
    
    # Fetch all embeddings for this paper
    embeddings_cursor = db.embeddings.find({"paper_id": paper_id})
    
    vectors = []
    metadata_list = []
    
    for doc in embeddings_cursor:
        if "embedding" not in doc:
            continue
            
        vectors.append(doc["embedding"])
        
        # Build metadata
        meta = {
            "chunk_id": str(doc["chunk_id"]),
            "paper_id": str(doc["paper_id"]),
            "user_id": str(doc["user_id"]),
            "page_start": doc.get("page_start", 0),
            "page_end": doc.get("page_end", 0),
        }
        
        # We also need the original text for retrieval.
        # Fetch it from chunks collection using chunk_id.
        chunk = db.chunks.find_one({"_id": doc["chunk_id"]}) if not isinstance(doc["chunk_id"], str) else db.chunks.find_one({"_id": doc["chunk_id"]})
        # Wait, chunk_id is a string in doc but we need to convert it back to ObjectId to fetch if it was stored as string.
        from bson import ObjectId
        
        try:
            chunk_obj_id = ObjectId(doc["chunk_id"])
        except:
            chunk_obj_id = doc["chunk_id"]
            
        chunk = db.chunks.find_one({"_id": chunk_obj_id})
        
        if chunk:
            meta["text"] = chunk.get("text", "")
            meta["section"] = chunk.get("section", "")
        else:
            meta["text"] = ""
            meta["section"] = ""
            
        metadata_list.append(meta)
        
    if not vectors:
        logger.warning(f"No valid embeddings found for paper {paper_id}")
        return []
        
    ids = await vector_store.add_embeddings(vectors, metadata_list)
    logger.info(f"Successfully added {len(ids)} vectors to FAISS for paper {paper_id}")
    return ids
