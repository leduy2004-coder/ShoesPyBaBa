from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.db.base import get_db
from app.middleware.authenticate import authenticate
from app.models.user_model import User
from app.services.review_service import ReviewService
from app.schemas.review_schema import ReviewCreate, ReviewUpdate, ReviewResponse
from app.schemas.common_schema import ResponseSchema
from app.schemas.base_schema import DataResponse
router = APIRouter()


security = HTTPBearer()
def current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    return authenticate(credentials, db)

@router.post("/reviews", tags=["reviews"], description="Create a new review", response_model=DataResponse[ReviewResponse])
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_user_dependency)
):
    service = ReviewService(db)
    review = service.create_review(current_user.id, data)
    return DataResponse.custom_response(
        code="201", 
        message="Review created successfully", 
        data=review)

@router.get("/reviews" , tags=["reviews"], description="Get reviews for a product", response_model=ResponseSchema[List[ReviewResponse]])
def get_reviews_by_product(
    product_id: int = Query(..., description="ID of the product"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    service = ReviewService(db)
    data, pagination = service.get_product_reviews(product_id, page, size)
    return ResponseSchema.custom_response(
        code="200",
        message="Reviews retrieved successfully",
        data=data,
        pagination=pagination
)

@router.get("/reviews/me", tags=["reviews"], description="Get my reviews", response_model=ResponseSchema[List[ReviewResponse]])
def get_my_reviews(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(current_user_dependency)
):
    service = ReviewService(db)
    data, pagination = service.get_my_reiviews(current_user.id, page, size)
    return ResponseSchema.custom_response(
        code="200",
        message="My reviews retrieved successfully",
        data=data,
        pagination=pagination
)

@router.put("/reviews/{review_id}", tags=["reviews"], description="Update a review", response_model=DataResponse[ReviewResponse])
def update_review(
    review_id: int,
    data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_user_dependency)
):
    service = ReviewService(db)
    update_review = service.update_review(current_user.id, review_id, data)
    return DataResponse.custom_response(
        code="200",
        message="Review updated successfully",
        data=update_review
    )

@router.delete("/reviews/{review_id}", tags=["reviews"], description="Delete a review", response_model=DataResponse[None])
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_user_dependency)
):
    service = ReviewService(db)
    service.delete_review(current_user.id, review_id)
    return DataResponse.custom_response(
        code="200",
        message="Review deleted successfully",
        data=None
    )

@router.get("/reviews/check-eligibility", tags=["reviews"], description="Check if user can review product")
def check_eligibility(
    product_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(current_user_dependency)
):
    service = ReviewService(db)
    result = service.check_eligibility(current_user.id, product_id)
    return DataResponse.custom_response(
        code="200",
        message="Eligibility checked",
        data=result
    )