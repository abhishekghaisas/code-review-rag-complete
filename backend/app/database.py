"""
Database models for storing code reviews
Using SQLAlchemy with SQLite (easily switchable to PostgreSQL)
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import json

# Database URL (SQLite by default, can switch to PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/reviews.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class CodeReview(Base):
    """Model for storing code reviews"""
    __tablename__ = "code_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Input data
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    use_rag = Column(Boolean, default=True)
    
    # Review result
    review_text = Column(Text, nullable=False)
    similar_code = Column(Text, nullable=True)  # JSON string
    similar_code_metadata = Column(Text, nullable=True)  # JSON string
    
    # Metadata
    model_used = Column(String(100), nullable=False)
    rag_enabled = Column(Boolean, default=False)
    context_used = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional: user tracking (for multi-user)
    user_id = Column(String(100), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "code": self.code,
            "language": self.language,
            "model": self.model,
            "use_rag": self.use_rag,
            "review": {
                "review": self.review_text,
                "similar_code": json.loads(self.similar_code) if self.similar_code else [],
                "similar_code_metadata": json.loads(self.similar_code_metadata) if self.similar_code_metadata else [],
                "model_used": self.model_used,
                "rag_enabled": self.rag_enabled,
                "context_used": self.context_used,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class IngestionJob(Base):
    """Model for tracking code ingestion jobs"""
    __tablename__ = "ingestion_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Job details
    job_type = Column(String(50), nullable=False)  # 'manual' or 'github'
    source = Column(Text, nullable=False)  # GitHub URL or 'manual input'
    
    # Results
    status = Column(String(50), nullable=False)  # 'pending', 'success', 'error'
    chunks_ingested = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Optional: user tracking
    user_id = Column(String(100), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "source": self.source,
            "status": self.status,
            "chunks_ingested": self.chunks_ingested,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# Create tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper functions
def save_review(db, code: str, language: str, model: str, use_rag: bool, review_response: dict):
    """Save a code review to database"""
    review = CodeReview(
        code=code,
        language=language,
        model=model,
        use_rag=use_rag,
        review_text=review_response.get("review", ""),
        similar_code=json.dumps(review_response.get("similar_code", [])),
        similar_code_metadata=json.dumps(review_response.get("similar_code_metadata", [])),
        model_used=review_response.get("model_used", model),
        rag_enabled=review_response.get("rag_enabled", False),
        context_used=review_response.get("context_used", False),
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db, limit: int = 20, skip: int = 0):
    """Get recent reviews"""
    return db.query(CodeReview).order_by(CodeReview.created_at.desc()).offset(skip).limit(limit).all()


def get_review_by_id(db, review_id: int):
    """Get a specific review by ID"""
    return db.query(CodeReview).filter(CodeReview.id == review_id).first()


def delete_review(db, review_id: int):
    """Delete a review"""
    review = get_review_by_id(db, review_id)
    if review:
        db.delete(review)
        db.commit()
        return True
    return False


def save_ingestion_job(db, job_type: str, source: str, status: str = "pending"):
    """Save an ingestion job"""
    job = IngestionJob(
        job_type=job_type,
        source=source,
        status=status,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def update_ingestion_job(db, job_id: int, status: str, chunks_ingested: int = 0, error_message: str = None):
    """Update ingestion job status"""
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if job:
        job.status = status
        job.chunks_ingested = chunks_ingested
        job.error_message = error_message
        job.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
    return job


def get_ingestion_jobs(db, limit: int = 20):
    """Get recent ingestion jobs"""
    return db.query(IngestionJob).order_by(IngestionJob.created_at.desc()).limit(limit).all()