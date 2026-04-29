"""
FastAPI application for Code Review RAG Assistant - Railway Deployment
"""

import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

from app.models import ReviewRequest, ReviewResponse
from app.rag_engine import CodeReviewRAG
from app.github_ingestion import GitHubIngestion

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
    allow_origins=["*"],  # Allow all for Railway deployment
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
    
    logger.info("🚀 Starting Code Review RAG Assistant...")
    
    try:
        # Initialize RAG engine
        rag_engine = CodeReviewRAG()
        logger.info("✅ RAG engine initialized")
        
        # Initialize GitHub ingestion
        github_ingestion = GitHubIngestion()
        logger.info("✅ GitHub ingestion initialized")
        
        logger.info("🎉 Code Review RAG Assistant is ready!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Code Review RAG Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "rag_engine": rag_engine is not None
    }


@app.post("/api/review", response_model=ReviewResponse)
async def review_code_endpoint(request: ReviewRequest):
    """Generate code review"""
    try:
        logger.info(f"Review: {request.language}, model={request.model}")
        
        result = await rag_engine.review_code(
            code=request.code,
            model=request.model,
            language=request.language,
            use_rag=request.use_rag
        )
        
        return ReviewResponse(**result)
        
    except Exception as e:
        logger.error(f"Review error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/ingest")
async def ingest_code_endpoint(request: dict):
    """Ingest code chunks OR GitHub repository"""
    try:
        # Handle GitHub repository URL
        if "repo_url" in request:
            repo_url = request["repo_url"]
            logger.info(f"Ingesting repository: {repo_url}")
            
            code_files = github_ingestion.ingest_repository(repo_url)
            
            for file in code_files:
                rag_engine.ingest_code(
                    code=file["code"],
                    filename=file["filename"],
                    language=file["language"]
                )
            
            return {
                "status": "success",
                "files_processed": len(code_files),
                "message": f"✅ Ingested {len(code_files)} files from repository"
            }
        
        # Handle code chunks
        elif "code_chunks" in request:
            code_chunks = request["code_chunks"]
            logger.info(f"Ingesting {len(code_chunks)} chunks")
            
            for chunk in code_chunks:
                rag_engine.ingest_code(
                    code=chunk.get("code", ""),
                    filename=chunk.get("filename", "unknown"),
                    language=chunk.get("language", "python")
                )
            
            return {
                "status": "success",
                "chunks_ingested": len(code_chunks)
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'repo_url' or 'code_chunks' required"
            )
        
    except Exception as e:
        logger.error(f"Ingest error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/api/ingest/repo")
async def ingest_repository(request: dict):
    """Ingest GitHub repository"""
    try:
        repo_url = request.get("repo_url")
        
        if not repo_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="repo_url is required"
            )
        
        logger.info(f"Ingesting repo: {repo_url}")
        
        code_files = github_ingestion.ingest_repository(repo_url)
        
        for file in code_files:
            rag_engine.ingest_code(
                code=file["code"],
                filename=file["filename"],
                language=file["language"]
            )
        
        return {
            "status": "success",
            "files_processed": len(code_files),
            "message": f"Successfully ingested {len(code_files)} files"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Repo ingest error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {
                "id": "claude-haiku-4-5-20251001",
                "name": "Claude Haiku 4.5",
                "provider": "Anthropic"
            },
            {
                "id": "claude-sonnet-4-20250514",
                "name": "Claude Sonnet 4",
                "provider": "Anthropic"
            }
        ]
    }


@app.get("/api/stats")
async def get_stats():
    """Get statistics"""
    try:
        return rag_engine.get_stats()
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return {"error": str(e)}


@app.delete("/api/reset")
async def reset_codebase():
    """Clear all ingested code"""
    try:
        rag_engine.clear_codebase()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)