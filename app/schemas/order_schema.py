from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class DeliveryAddressSchema(BaseModel):
    street_address: str
    ward: Optional[str] = None
    province_city: str
    recipient_name: str
    recipient_phone: str


class OrderItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: int
    product_id: int
    product_name: str
    product_image: Optional[str] = None
    size: Optional[int] = None
    color: Optional[str] = None
    quantity: int
    price_at_purchase: float


class CreateOrderItemSchema(BaseModel):
    product_id: int
    product_name: str
    size: Optional[int] = None
    color: Optional[str] = None
    quantity: int
    price_at_purchase: float


class OrderSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    user_full_name: Optional[str] = None
    delivery_address: Dict[str, Any]  # JSON field
    order_date: datetime
    total_amount: float
    status: str
    payment_status: str
    payment_intent_id: Optional[str] = None
    payment_method: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: Optional[List[OrderItemSchema]] = None


class DirectOrderItemSchema(BaseModel):
    """Schema for direct order item (buy now)"""
    product_id: int
    quantity: int
    size: Optional[int] = None
    color: Optional[str] = None


class CreateDirectOrderSchema(BaseModel):
    """Schema for creating order directly from products (buy now)"""
    items: List[DirectOrderItemSchema]
    delivery_address: DeliveryAddressSchema


class CreateOrderFromCartSchema(BaseModel):
    """Schema for creating order from cart"""
    delivery_address: DeliveryAddressSchema


class OrderSearchSchema(BaseModel):
    """Schema for order search filters"""
    user_id: Optional[int] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    limit: int = 10


class OrderHistorySchema(BaseModel):
    """Schema for admin order history"""
    orders: List[OrderSchema]
    total: int
    page: int
    limit: int
    total_pages: int


class CreateOrderSchema(BaseModel):
    delivery_address: DeliveryAddressSchema
    items: List[CreateOrderItemSchema]


class UpdateOrderSchema(BaseModel):
    delivery_address: Optional[DeliveryAddressSchema] = None
    status: Optional[str] = None
    total_amount: Optional[float] = None

