from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class CartItemSchema(BaseModel):
    """Schema for cart item response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    cart_id: int
    product_id: int
    quantity: int
    size: Optional[int] = None
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AddToCartSchema(BaseModel):
    """Schema for adding/updating item in cart"""
    product_id: int
    quantity: int = 1
    size: int
    color: str


class CartItemWithProductSchema(BaseModel):
    """Cart item with product details"""
    id: int
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    quantity: int
    size: Optional[int] = None
    color: Optional[str] = None
    current_price: float  # Current price from product
    subtotal: float


class CartSchema(BaseModel):
    """Complete cart with items and total"""
    id: int
    user_id: int
    items: List[CartItemWithProductSchema]
    total_items: int
    total_amount: float
    created_at: datetime
    updated_at: datetime
