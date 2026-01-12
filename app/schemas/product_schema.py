from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


from app.schemas.file_schema import FileProductResponse


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
    image_urls: Optional[List[FileProductResponse]] = None
    variants: Optional[List[Dict[str, Any]]] = None
    deleted_at: Optional[datetime] = None
    sold_count: int = 0


class ProductPaginationSchema(BaseModel):
    items: List[ProductSchema]
    total: int
    page: int
    limit: int
    total_pages: int


class CreateProductSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    status: str = "active"
    image_urls: Optional[List[FileProductResponse]] = None
    variants: Optional[List[ProductVariantSchema]] = None


class UpdateProductSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    status: Optional[str] = None
    image_urls: Optional[List[FileProductResponse]] = None
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
    sold_count: int = 0
    
    class Config:
        from_attributes = True

class ProductResponseDetail(BaseModel):
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
    sort_by: Optional[str] = None
    status: Optional[str] = None

    sort_by: Optional[
        Literal["price_asc", "price_desc", "newest"]
    ] = "newest"