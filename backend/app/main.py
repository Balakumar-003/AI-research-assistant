from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.api import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_to_mongo()
    yield
    # Shutdown
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
