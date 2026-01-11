from pydantic import BaseModel
from typing import Optional, List
from app.schemas.order_schema import DeliveryAddressSchema, DirectOrderItemSchema


class CreatePaymentIntentSchema(BaseModel):
    amount: float
    currency: str = "vnd"

class PaymentIntentResponseSchema(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str
    status: str


class ConfirmPaymentFromCartSchema(BaseModel):
    payment_intent_id: str
    delivery_address: DeliveryAddressSchema


class ConfirmPaymentFromProductsSchema(BaseModel):
    payment_intent_id: str
    items: List[DirectOrderItemSchema]
    delivery_address: DeliveryAddressSchema
