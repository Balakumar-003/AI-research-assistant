from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.api import auth

from app.providers.embedding_provider import embedding_provider
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import validation_exception_handler, http_exception_handler, general_exception_handler
from app.core.logger import logger
import time
import uuid
from fastapi import Request

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
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS Middleware
origins = settings.CORS_ORIGINS.split(",") if isinstance(settings.CORS_ORIGINS, str) else settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    response = await call_next(request)
    
    duration_ms = (time.time() - start_time) * 1000
    
    logger.info(
        f"Handled request {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms
        }
    )
    
    response.headers["X-Request-ID"] = request_id
    return response

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
from app.api import reports
app.include_router(reports.router, prefix="/api", tags=["Reports"])
from app.api import health
app.include_router(health.router, tags=["Health"])

@app.get("/")
async def root():
    """
    Root endpoint to verify the API is reachable.
    """
    return {
        "message": "Welcome to AI Research Assistant API",
        "status": "running"
    }
