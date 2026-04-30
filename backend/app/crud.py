"""
CRUD operations for database
"""

from sqlalchemy.orm import Session
from app.database import Review
from datetime import datetime


def create_review(
    db: Session,
    code: str,
    language: str,
    review: str,
    model_used: str,
    rag_enabled: bool = False
) -> Review:
    """Create a new review in the database"""
    db_review = Review(
        code=code,
        language=language,
        review=review,
        model_used=model_used,
        rag_enabled=rag_enabled,
        created_at=datetime.utcnow()
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review


def get_review(db: Session, review_id: int) -> Review:
    """Get a single review by ID"""
    return db.query(Review).filter(Review.id == review_id).first()


def get_reviews(db: Session, skip: int = 0, limit: int = 50) -> list[Review]:
    """Get all reviews with pagination"""
    return db.query(Review).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()


def delete_review(db: Session, review_id: int) -> bool:
    """Delete a review by ID"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if review:
        db.delete(review)
        db.commit()
        return True
    return False


def delete_all_reviews(db: Session) -> int:
    """Delete all reviews"""
    count = db.query(Review).count()
    db.query(Review).delete()
    db.commit()
    return count