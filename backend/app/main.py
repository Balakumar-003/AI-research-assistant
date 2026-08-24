from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.api import auth

from app.providers.embedding_provider import embedding_provider

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_to_mongo()
    embedding_provider.load()
    
    # Import here to avoid circular imports during startup
    from app.services.vector_service import vector_store
    
    yield
    # Shutdown
    vector_store.save()
    close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for the Enterprise AI Research Assistant.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include Routers
app.include_router(auth.router, tags=["Authentication"])
from app.api import projects
app.include_router(projects.router, tags=["Projects"])
from app.api import papers
app.include_router(papers.router, tags=["Papers"])
from app.api import chunks
app.include_router(chunks.router, tags=["Chunks"])
from app.api import embeddings
app.include_router(embeddings.router, tags=["Embeddings"])
from app.api import search_routes
app.include_router(search_routes.router, tags=["Search"])
from app.api import chat_routes
app.include_router(chat_routes.router, tags=["Chat"])
from app.api import agent_routes
app.include_router(agent_routes.router, prefix="/research", tags=["Agent"])
from app.api import comparisons
app.include_router(comparisons.router, prefix="/api/comparisons", tags=["Comparisons"])
from app.api import literature_reviews
app.include_router(literature_reviews.router, prefix="/api/literature-reviews", tags=["Literature Reviews"])
from app.api import research_gaps
app.include_router(research_gaps.router, prefix="/api/research-gaps", tags=["Research Gaps"])
from app.api import research_questions
app.include_router(research_questions.router, prefix="/api", tags=["Research Questions"])
from app.api import research_proposals
app.include_router(research_proposals.router, prefix="/api", tags=["Research Proposals"])
from app.api import experiments
app.include_router(experiments.router, prefix="/api", tags=["Experiments"])

@app.get("/")
async def root():
    """
    Root endpoint to verify the API is reachable.
    """
    return {
        "message": "Welcome to AI Research Assistant API",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for deployment monitoring.
    """
    return {
        "status": "healthy"
    }
