import pytest
import os
import shutil
import asyncio
from app.rag.vector_store import VectorDBService

@pytest.fixture
def temp_vector_store():
    # Setup temporary paths
    index_path = "test_vector_store/test.index"
    metadata_path = "test_vector_store/test_metadata.pkl"
    
    # Ensure directory is clean
    if os.path.exists("test_vector_store"):
        shutil.rmtree("test_vector_store")
        
    store = VectorDBService(dim=3, index_path=index_path, metadata_path=metadata_path)
    yield store
    
    # Teardown
    if os.path.exists("test_vector_store"):
        shutil.rmtree("test_vector_store")

@pytest.mark.asyncio
async def test_add_and_search(temp_vector_store):
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    metadata = [
        {"chunk_id": "c1", "paper_id": "p1", "user_id": "u1", "text": "Paper 1 text"},
        {"chunk_id": "c2", "paper_id": "p2", "user_id": "u2", "text": "Paper 2 text"}
    ]
    
    ids = await temp_vector_store.add_embeddings(embeddings, metadata)
    assert len(ids) == 2
    
    # Search with exact match to first vector
    results = await temp_vector_store.search([1.0, 0.0, 0.0], top_k=1)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "c1"

@pytest.mark.asyncio
async def test_search_filtering(temp_vector_store):
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0]
    ]
    metadata = [
        {"chunk_id": "c1", "paper_id": "p1", "user_id": "u1"},
        {"chunk_id": "c2", "paper_id": "p2", "user_id": "u2"}
    ]
    
    await temp_vector_store.add_embeddings(embeddings, metadata)
    
    # Filter by user_id
    results_u2 = await temp_vector_store.search([1.0, 0.0, 0.0], top_k=2, user_id="u2")
    assert len(results_u2) == 1
    assert results_u2[0]["chunk_id"] == "c2"

@pytest.mark.asyncio
async def test_delete_by_paper(temp_vector_store):
    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    metadata = [
        {"chunk_id": "c1", "paper_id": "p1", "user_id": "u1"},
        {"chunk_id": "c2", "paper_id": "p2", "user_id": "u1"}
    ]
    
    await temp_vector_store.add_embeddings(embeddings, metadata)
    assert temp_vector_store.get_stats()["total_vectors"] == 2
    
    deleted_count = await temp_vector_store.delete_by_paper("p1")
    assert deleted_count == 1
    
    # Check stats
    stats = temp_vector_store.get_stats()
    assert stats["total_vectors"] == 1
    
    # Check search
    results = await temp_vector_store.search([1.0, 0.0, 0.0], top_k=5)
    assert len(results) == 1
    assert results[0]["chunk_id"] == "c2"

@pytest.mark.asyncio
async def test_save_load(temp_vector_store):
    embeddings = [[1.0, 0.0, 0.0]]
    metadata = [{"chunk_id": "c1", "paper_id": "p1", "user_id": "u1"}]
    
    await temp_vector_store.add_embeddings(embeddings, metadata)
    temp_vector_store.save()
    
    # Load into a new store
    new_store = VectorDBService(
        dim=3,
        index_path=temp_vector_store.index_path,
        metadata_path=temp_vector_store.metadata_path
    )
    
    stats = new_store.get_stats()
    assert stats["total_vectors"] == 1
    
    results = await new_store.search([1.0, 0.0, 0.0], top_k=1)
    assert results[0]["chunk_id"] == "c1"
