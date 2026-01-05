from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewCreate(BaseModel):
    product_id: int
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    comment: Optional[str] = None

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True