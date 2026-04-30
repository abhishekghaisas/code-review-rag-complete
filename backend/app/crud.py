"""
CRUD operations for database
"""

from sqlalchemy.orm import Session
from app.database import CodeReview
from datetime import datetime


def create_review(
    db: Session,
    code: str,
    language: str,
    review: str,
    model_used: str,
    rag_enabled: bool = False
) -> CodeReview:
    """Create a new review in the database"""
    db_review = CodeReview(
        code=code,
        language=language,
        model=model_used,  # Store in model field
        review_text=review,
        model_used=model_used,
        rag_enabled=rag_enabled,
        use_rag=rag_enabled,
        context_used=rag_enabled,
        created_at=datetime.utcnow()
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review


def get_review(db: Session, review_id: int) -> CodeReview:
    """Get a single review by ID"""
    return db.query(CodeReview).filter(CodeReview.id == review_id).first()


def get_reviews(db: Session, skip: int = 0, limit: int = 50) -> list[CodeReview]:
    """Get all reviews with pagination"""
    return db.query(CodeReview).order_by(CodeReview.created_at.desc()).offset(skip).limit(limit).all()


def delete_review(db: Session, review_id: int) -> bool:
    """Delete a review by ID"""
    review = db.query(CodeReview).filter(CodeReview.id == review_id).first()
    if review:
        db.delete(review)
        db.commit()
        return True
    return False


def delete_all_reviews(db: Session) -> int:
    """Delete all reviews"""
    count = db.query(CodeReview).count()
    db.query(CodeReview).delete()
    db.commit()
    return count