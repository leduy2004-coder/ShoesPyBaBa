from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models.review_model import Review

class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, review_id: int):
        return self.db.query(Review).filter(
            Review.id == review_id,
            Review.deleted_at.is_(None)
        ).first()

    def get_by_user_and_product(self, user_id: int, product_id: int):
        return self.db.query(Review).filter(
            Review.user_id == user_id,
            Review.product_id == product_id,
            Review.deleted_at.is_(None)
        ).first()
    
    def get_by_product_id(self, product_id: int, skip: int, limit: int):
        query = self.db.query(Review).filter(
            Review.product_id == product_id,
            Review.deleted_at.is_(None)
        )
        total = query.count()
        reviews = query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
        return total, reviews
    
    def get_by_user_id(self, user_id: int, skip: int, limit: int):
        query - self.db.query(Review).filter(
            Review.user_id == user_id,
            Review.deleted_at.is_(None)
        )
        total = query.count()
        reviews = query.order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
        return total, reviews
    
    def create(self, user_id: int, data: dict):
        new_review = Review(
            user_id=user_id,
            product_id=data['product_id'],
            rating=data['rating'],
            comment=data.get('comment'),
            created_at=datetime.now(),
        )
        self.db.add(new_review)
        self.db.commit()
        self.db.refresh(new_review)
        return new_review
    
    def update(self, review: Review, data: dict):
        if 'rating' in data and data['rating'] is not None:
            review.rating = data['rating']
        if 'comment' in data and data['comment'] is not None:
            review.comment = data['comment']
        
        review.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(review)
        return review
    
    def delete(self, review: Review):
        review.deleted_at = datetime.now()
        self.db.commit()
        self.db.refresh(review)