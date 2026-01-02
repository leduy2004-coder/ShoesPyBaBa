from app.models.base_model import BaseModel
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, JSON

import datetime

class Product(BaseModel):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(String(500))  # Removed index to avoid key length limit
    price = Column(Float, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True, index=True)
    status = Column(String(50), index=True, default="active")  # active, inactive, out_of_stock
    image_urls = Column(JSON, nullable=True)  # List of image URLs
    variants = Column(JSON, nullable=True)  # List of ProductVariant objects
    deleted_at = Column(DateTime, index=True, nullable=True)
    
