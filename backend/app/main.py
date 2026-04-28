"""
FastAPI application for Code Review RAG Assistant
WITH DATABASE INTEGRATION
"""

import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import Session

from .models import (
    ReviewRequest, ReviewResponse,
    IngestRequest, IngestResponse,
    ModelsResponse, StatsResponse, HealthResponse
)
from .rag_engine import CodeReviewRAG
from .database import init_db, get_db, save_review, get_reviews, get_review_by_id, delete_review, get_ingestion_jobs, save_ingestion_job, update_ingestion_job

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
    description="AI-powered code review using RAG and Anthropic Claude",
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

# Global RAG engine instance
rag_engine: CodeReviewRAG = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine and database on startup"""
    global rag_engine
    
    logger.info("Starting up Code Review RAG Assistant...")
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("✅ Database initialized")
    
    try:
        # Initialize RAG engine
        db_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        collection_name = os.getenv("COLLECTION_NAME", "code_chunks")
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        rag_engine = CodeReviewRAG(
            db_path=db_path,
            collection_name=collection_name,
            embedding_model=embedding_model
        )
        
        logger.info("✅ RAG engine initialized successfully")
        logger.info(f"📊 Database stats: {rag_engine.get_stats()}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG engine: {str(e)}")
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
            "reviews": "/api/reviews",
            "ingest": "/api/ingest",
            "models": "/api/models",
            "stats": "/api/stats"
        },
        "github": "https://github.com/yourusername/code-review-rag"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check if RAG engine is initialized
        db_connected = rag_engine is not None
        llm_initialized = rag_engine.llm is not None if db_connected else False
        
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
async def review_code_endpoint(request: ReviewRequest, db: Session = Depends(get_db)):
    """
    Generate code review with RAG - NOW SAVES TO DATABASE!
    """
    try:
        logger.info(f"Review request: language={request.language}, model={request.model}, rag={request.use_rag}")
        
        # Generate review using RAG engine
        result = rag_engine.review_code(
            code=request.code,
            language=request.language,
            model=request.model,
            use_rag=request.use_rag,
            n_similar=request.n_similar
        )
        
        # Check for errors in result
        if "error" in result and result["error"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        # Save to database
        saved_review = save_review(
            db=db,
            code=request.code,
            language=request.language,
            model=request.model,
            use_rag=request.use_rag,
            review_response=result
        )
        
        # Add database ID to response
        result["id"] = saved_review.id
        logger.info(f"Review saved to database with ID: {saved_review.id}")
        
        return ReviewResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in review endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate review: {str(e)}"
        )


@app.get("/api/reviews")
async def list_reviews(limit: int = 20, skip: int = 0, db: Session = Depends(get_db)):
    """Get review history from database"""
    try:
        reviews = get_reviews(db, limit=limit, skip=skip)
        return {
            "reviews": [review.to_dict() for review in reviews],
            "total": len(reviews)
        }
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reviews: {str(e)}"
        )


@app.get("/api/reviews/{review_id}")
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """Get a specific review by ID"""
    try:
        review = get_review_by_id(db, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review {review_id} not found"
            )
        return review.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch review: {str(e)}"
        )


@app.delete("/api/reviews/{review_id}")
async def delete_review_endpoint(review_id: int, db: Session = Depends(get_db)):
    """Delete a review by ID"""
    try:
        success = delete_review(db, review_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review {review_id} not found"
            )
        return {"status": "success", "message": f"Review {review_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete review: {str(e)}"
        )


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_code(request: IngestRequest, db: Session = Depends(get_db)):
    """Ingest code into vector database"""
    job = None
    try:
        # Check if code_chunks provided
        if request.code_chunks:
            logger.info(f"Ingesting {len(request.code_chunks)} code chunks...")
            
            # Create ingestion job
            job = save_ingestion_job(db, job_type="manual", source="manual_input", status="pending")
            
            # Convert Pydantic models to dicts
            chunks = [chunk.model_dump() for chunk in request.code_chunks]
            
            # Ingest into RAG engine
            result = rag_engine.ingest_code(chunks)
            
            # Update job status
            update_ingestion_job(db, job.id, status="success", chunks_ingested=result.get("chunks_ingested", 0))
            
            return IngestResponse(**result)
        
        # Check if repo_url provided
        elif request.repo_url:
            logger.info(f"Ingesting repository: {request.repo_url}")
            
            # Create ingestion job
            job = save_ingestion_job(db, job_type="github", source=request.repo_url, status="pending")
            
            # Import here to avoid issues if GitPython not installed
            from .github_ingestion import GitHubIngestion
            
            # Initialize GitHub ingestion
            github = GitHubIngestion(max_file_size_mb=10)
            
            # Process repository (clone, extract, chunk)
            chunks = github.process_repository(
                repo_url=request.repo_url,
                chunk_size=1000,
                chunk_overlap=100
            )
            
            logger.info(f"Processed repository into {len(chunks)} chunks")
            
            # Ingest into RAG engine
            result = rag_engine.ingest_code(chunks)
            
            # Update job status
            update_ingestion_job(db, job.id, status="success", chunks_ingested=result.get("chunks_ingested", 0))
            
            return IngestResponse(**result)
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either repo_url or code_chunks must be provided"
            )
            
    except HTTPException:
        if job:
            update_ingestion_job(db, job.id, status="error", error_message="Bad request")
        raise
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {str(e)}")
        if job:
            update_ingestion_job(db, job.id, status="error", error_message=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest code: {str(e)}"
        )


@app.get("/api/ingestion/jobs")
async def list_ingestion_jobs(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent ingestion jobs"""
    try:
        jobs = get_ingestion_jobs(db, limit=limit)
        return {
            "jobs": [job.to_dict() for job in jobs],
            "total": len(jobs)
        }
    except Exception as e:
        logger.error(f"Error fetching ingestion jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ingestion jobs: {str(e)}"
        )


@app.get("/api/models")
async def list_models():
    """Get list of available Claude models"""
    try:
        models_data = rag_engine.llm.get_available_models()
        return models_data
    except Exception as e:
        logger.error(f"Error in models endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch models: {str(e)}"
        )


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get statistics about the vector database"""
    try:
        stats = rag_engine.get_stats()
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=stats["error"]
            )
        
        return StatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in stats endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@app.delete("/api/reset")
async def reset_database():
    """Reset the vector database (DANGER: Deletes all data!)"""
    try:
        logger.warning("⚠️ Database reset requested")
        rag_engine.reset_database()
        
        return {
            "status": "success",
            "message": "Database reset successfully",
            "warning": "All data has been deleted"
        }
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset database: {str(e)}"
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
