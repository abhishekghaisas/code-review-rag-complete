"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ReviewRequest(BaseModel):
    """Request model for code review"""
    code: str = Field(..., description="Code snippet to review")
    language: str = Field(default="python", description="Programming language")
    model: str = Field(
        default="claude-haiku-4-5-20251001",
        description="Claude model ID to use"
    )
    use_rag: bool = Field(
        default=True,
        description="Whether to use RAG retrieval for context"
    )
    n_similar: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of similar code examples to retrieve"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "def calculate_total(items):\n    total = 0\n    for item in items:\n        total = total + item\n    return total",
                "language": "python",
                "model": "claude-haiku-4-5-20251001",
                "use_rag": True,
                "n_similar": 3
            }
        }


class SimilarCodeItem(BaseModel):
    """Model for a similar code item"""
    code: str
    metadata: Dict
    similarity_score: Optional[float] = None


class ReviewResponse(BaseModel):
    """Response model for code review"""
    review: str = Field(..., description="Generated code review")
    similar_code: List[str] = Field(default=[], description="Similar code snippets found")
    similar_code_metadata: List[Dict] = Field(default=[], description="Metadata for similar code")
    model_used: str = Field(..., description="Model used for generation")
    rag_enabled: bool = Field(..., description="Whether RAG was used")
    context_used: bool = Field(..., description="Whether context was provided to LLM")
    error: Optional[str] = Field(None, description="Error message if any")


class CodeChunk(BaseModel):
    """Model for a code chunk to ingest"""
    id: str = Field(..., description="Unique identifier for this chunk")
    code: str = Field(..., description="Code content")
    language: str = Field(..., description="Programming language")
    metadata: Dict = Field(default={}, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "repo1_file1_func1",
                "code": "def hello_world():\n    print('Hello, World!')",
                "language": "python",
                "metadata": {
                    "file_path": "src/greetings.py",
                    "function_name": "hello_world",
                    "repo": "my-project"
                }
            }
        }


class IngestRequest(BaseModel):
    """Request model for code ingestion"""
    repo_url: Optional[str] = Field(None, description="GitHub repository URL to clone and ingest")
    code_chunks: Optional[List[CodeChunk]] = Field(
        None,
        description="Pre-processed code chunks to ingest directly"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_url": "https://github.com/username/repo"
            }
        }


class IngestResponse(BaseModel):
    """Response model for code ingestion"""
    status: str = Field(..., description="Status of ingestion (success/error)")
    message: Optional[str] = Field(None, description="Additional message")
    chunks_ingested: Optional[int] = Field(None, description="Number of chunks ingested")
    collection_size: Optional[int] = Field(None, description="Total collection size after ingestion")


class ModelInfo(BaseModel):
    """Information about a model"""
    id: str
    name: str
    cost: str
    quality: Optional[str] = None
    description: Optional[str] = None


class ModelsResponse(BaseModel):
    """Response model for available models"""
    free_models: List[ModelInfo]
    paid_models: List[ModelInfo]


class StatsResponse(BaseModel):
    """Response model for database statistics"""
    collection_name: str
    total_chunks: int
    embedding_model: str
    embedding_dimension: int
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database_connected: bool
    llm_client_initialized: bool
