from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class BrandSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    brand_name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BrandPaginationSchema(BaseModel):
    items: List[BrandSchema]
    total: int
    page: int
    limit: int
    total_pages: int



class CreateBrandSchema(BaseModel):
    brand_name: str
    description: Optional[str] = None


class UpdateBrandSchema(BaseModel):
    brand_name: Optional[str] = None
    description: Optional[str] = None

