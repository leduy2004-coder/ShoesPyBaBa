from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
import stripe
from app.db.base import get_db
from app.services.payment_service import PaymentService
from app.schemas.payment_schema import (
    CreatePaymentIntentSchema,
    PaymentIntentResponseSchema,
    ConfirmPaymentFromCartSchema,
    ConfirmPaymentFromProductsSchema
)

from app.schemas.order_schema import OrderSchema, DeliveryAddressSchema
from app.core.security import get_current_user

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/create-intent", response_model=PaymentIntentResponseSchema)
async def create_payment_intent(
    amount: int,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """Create Stripe payment intent for cart total"""
    return PaymentService.create_payment_intent(amount)


@router.post("/confirm-from-cart", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def confirm_payment_from_cart(
    data: ConfirmPaymentFromCartSchema,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Confirm payment and create order from cart"""
    return PaymentService.confirm_payment_from_cart(db, current_user["user_id"], data)


@router.post("/confirm-from-products", response_model=OrderSchema, status_code=status.HTTP_201_CREATED)
async def confirm_payment_from_products(
    data: ConfirmPaymentFromProductsSchema,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Confirm payment and create order from products (buy now)"""
    return PaymentService.confirm_payment_from_products(db, current_user["user_id"], data)


@router.post("/test-confirm/{payment_intent_id}")
async def test_confirm_payment(
    payment_intent_id: str,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    TEST ONLY: Auto confirm payment on Stripe using test card.
    After this, call /confirm-from-cart or /confirm-from-products to create order.
    """
    return PaymentService.test_confirm_payment(payment_intent_id)



