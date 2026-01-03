from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductVariantSchema(BaseModel):
    color: str
    size: int
    stock_quantity: int


class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    status: str = "active"
    image_urls: Optional[List[str]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    deleted_at: Optional[datetime] = None


class CreateProductSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    status: str = "active"
    image_urls: Optional[List[str]] = None
    variants: Optional[List[ProductVariantSchema]] = None


class UpdateProductSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    status: Optional[str] = None
    image_urls: Optional[List[str]] = None
    variants: Optional[List[ProductVariantSchema]] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    status: str = "active"
    image_urls: Optional[List[str]] = None
    variants: Optional[List[ProductVariantSchema]] = None
    
    class Config:
        from_attributes = True

class ProductFilter(BaseModel):
    keyword: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    status: Optional[str] = None