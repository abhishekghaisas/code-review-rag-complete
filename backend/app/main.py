"""
FastAPI application for Code Review RAG Assistant
"""

import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

from app.models import (
    ReviewRequest, ReviewResponse,
    IngestRequest, IngestResponse,
    ModelsResponse, StatsResponse, HealthResponse
)
from app.rag_engine import CodeReviewRAG
from app.github_ingestion import GitHubIngestion
from app.database import init_db, get_db
from app import crud

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Code Review RAG Assistant",
    description="AI-powered code review using RAG and Claude API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_engine: CodeReviewRAG = None
github_ingestion: GitHubIngestion = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global rag_engine, github_ingestion
    
    logger.info("Starting up Code Review RAG Assistant...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        logger.info("✅ Database initialized")
        
        # Initialize RAG engine (simplified - no parameters needed)
        logger.info("Initializing RAG engine...")
        rag_engine = CodeReviewRAG()
        logger.info("✅ RAG engine initialized")
        
        # Initialize GitHub ingestion
        github_ingestion = GitHubIngestion()
        logger.info("✅ GitHub ingestion initialized")
        
        logger.info("🚀 Code Review RAG Assistant is ready!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Code Review RAG Assistant...")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Code Review RAG Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "review": "/api/review",
            "ingest": "/api/ingest",
            "ingest_repo": "/api/ingest/repo",
            "models": "/api/models",
            "stats": "/api/stats",
            "history": "/api/history"
        },
        "github": "https://github.com/abhishekghaisas/code-review-rag-complete"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        db_connected = rag_engine is not None
        llm_initialized = rag_engine.claude_client is not None if db_connected else False
        
        return HealthResponse(
            status="healthy" if db_connected and llm_initialized else "degraded",
            version="1.0.0",
            database_connected=db_connected,
            llm_client_initialized=llm_initialized
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/api/review", response_model=ReviewResponse)
async def review_code_endpoint(request: ReviewRequest):
    """
    Generate code review with optional RAG
    
    - **code**: Code snippet to review (required)
    - **language**: Programming language (default: python)
    - **model**: Claude model (default: claude-haiku-4-5-20251001)
    - **use_rag**: Whether to use RAG retrieval (default: false)
    """
    try:
        logger.info(f"Review request: language={request.language}, model={request.model}, rag={request.use_rag}")
        
        # Generate review
        result = await rag_engine.review_code(
            code=request.code,
            model=request.model,
            language=request.language,
            use_rag=request.use_rag
        )
        
        # Save to database
        db = next(get_db())
        try:
            crud.create_review(
                db=db,
                code=request.code,
                review=result["review"],
                model=result["model"],
                language=request.language
            )
        except Exception as e:
            logger.warning(f"Failed to save review to database: {e}")
        
        return ReviewResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in review endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate review: {str(e)}"
        )


@app.post("/api/ingest")
async def ingest_code_endpoint(request: IngestRequest):
    """
    Ingest code chunks into RAG system
    """
    try:
        if not request.code_chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="code_chunks required"
            )
        
        logger.info(f"Ingesting {len(request.code_chunks)} chunks...")
        
        for chunk in request.code_chunks:
            rag_engine.ingest_code(
                code=chunk.code,
                filename=chunk.get("filename", "unknown"),
                language=chunk.get("language", "python")
            )
        
        return {
            "status": "success",
            "chunks_ingested": len(request.code_chunks),
            "message": f"Successfully ingested {len(request.code_chunks)} code chunks"
        }
        
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest code: {str(e)}"
        )


@app.post("/api/ingest/repo")
async def ingest_repository(repo_url: str):
    """
    Ingest code from a GitHub repository
    """
    try:
        logger.info(f"Ingesting repository: {repo_url}")
        
        # Extract code files from repo
        code_files = github_ingestion.ingest_repository(repo_url)
        
        # Ingest each file
        chunks_ingested = 0
        for file in code_files:
            rag_engine.ingest_code(
                code=file["code"],
                filename=file["filename"],
                language=file["language"]
            )
            chunks_ingested += 1
        
        return {
            "status": "success",
            "repo_url": repo_url,
            "files_processed": len(code_files),
            "chunks_ingested": chunks_ingested
        }
        
    except Exception as e:
        logger.error(f"Error ingesting repository: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest repository: {str(e)}"
        )


@app.get("/api/models")
async def list_models():
    """Get list of available Claude models"""
    return {
        "models": [
            {
                "id": "claude-haiku-4-5-20251001",
                "name": "Claude Haiku 4.5",
                "cost_per_review": 0.002,
                "speed": "fast"
            },
            {
                "id": "claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4",
                "cost_per_review": 0.015,
                "speed": "medium"
            },
            {
                "id": "claude-opus-4-20250514",
                "name": "Claude Opus 4",
                "cost_per_review": 0.075,
                "speed": "slow"
            }
        ]
    }


@app.get("/api/stats")
async def get_stats():
    """Get RAG system statistics"""
    try:
        stats = rag_engine.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@app.get("/api/history")
async def get_history(limit: int = 10):
    """Get review history from database"""
    try:
        db = next(get_db())
        reviews = crud.get_recent_reviews(db, limit=limit)
        return {"reviews": reviews}
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get history: {str(e)}"
        )


@app.delete("/api/reset")
async def reset_codebase():
    """Reset the RAG codebase (clears all ingested code)"""
    try:
        rag_engine.clear_codebase()
        return {
            "status": "success",
            "message": "Codebase cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error resetting codebase: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset codebase: {str(e)}"
        )


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )