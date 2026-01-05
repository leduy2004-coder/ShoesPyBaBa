from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.review_repository import ReviewRepository
from app.schemas.review_schema import ReviewCreate, ReviewUpdate
from app.schemas.common_schema import PaginationSchema

class ReviewService:
    def __init__(self, db: Session):
        self.review_repository = ReviewRepository(db)

    def create_review(self, user_id: int, data: ReviewCreate):
        existing_review = self.review_repository.get_by_user_and_product(user_id, data.product_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has already reviewed this product."
            )
        return self.review_repository.create(user_id, data.model_dump())
    
    def get_product_reviews(self, product_id: int, page: int, size: int):
       skip = (page - 1) * size
       reviews, total = self.review_repository.get_by_product_id(product_id, skip, size)
       pagination = PaginationSchema(
           page=page, size=size, total=total,
           total_pages=(total + size - 1) // size
       )
       return reviews, pagination
    
    def get_my_reiviews(self, user_id: int, page: int, size: int):
        skip = (page - 1) * size
        reviews, total = self.review_repository.get_by_user_id(user_id, skip, size)
        pagination = PaginationSchema(
            page=page, size=size, total=total,
            total_pages=(total + size - 1) // size
        )
        return reviews, pagination
    
    def get_own_review(self, user_id: int, review_id: int):
        review = self.review_repository.get_by_id(review_id)
        if not review or review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found."
            )
        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this review."
            )
        return review
    
    def update_review(self, user_id: int, review_id: int, data: ReviewUpdate):
        review = self.get_own_review(user_id, review_id)
        return self.review_repository.update(review, data.model_dump(exclude_unset=True))
    
    def delete_review(self, user_id: int, review_id: int):
        review = self.get_own_review(user_id, review_id)
        self.review_repository.delete(review)