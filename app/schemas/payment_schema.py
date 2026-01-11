from pydantic import BaseModel
from typing import Optional, List
from app.schemas.order_schema import DeliveryAddressSchema, DirectOrderItemSchema


class CreatePaymentIntentSchema(BaseModel):
    """Schema for creating Stripe payment intent"""
    amount: float  # Amount in currency (will be converted to cents)
    currency: str = "vnd"

class PaymentIntentResponseSchema(BaseModel):
    """Response schema for payment intent"""
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str
    status: str


class ConfirmPaymentFromCartSchema(BaseModel):
    """Schema for confirming payment and creating order from cart"""
    payment_intent_id: str
    delivery_address: DeliveryAddressSchema


class ConfirmPaymentFromProductsSchema(BaseModel):
    """Schema for confirming payment and creating order from products"""
    payment_intent_id: str
    items: List[DirectOrderItemSchema]
    delivery_address: DeliveryAddressSchema
