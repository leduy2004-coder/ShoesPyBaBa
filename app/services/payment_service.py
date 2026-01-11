import stripe
import os
from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.payment_schema import (
    CreatePaymentIntentSchema,
    PaymentIntentResponseSchema,
    ConfirmPaymentFromCartSchema,
    ConfirmPaymentFromProductsSchema
)

from app.schemas.order_schema import DeliveryAddressSchema
from app.schemas.order_schema import CreateOrderFromCartSchema, OrderSchema
from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository

from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

# Configure Stripe
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
if STRIPE_KEY:
    stripe.api_key = STRIPE_KEY
else:
    stripe.api_key = None

class PaymentService:
    @staticmethod
    def _verify_payment_succeeded(payment_intent_id: str):
        """Helper to verify that a payment intent actually succeeded on Stripe"""
        if not stripe.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe API key not configured."
            )
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if payment_intent.status != "succeeded":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment not completed. Status: {payment_intent.status}"
                )
            return payment_intent
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )

    @staticmethod
    def _check_existing_order(db: Session, payment_intent_id: str):
        """Ensure no order has already been created for this payment intent"""
        existing_order = OrderRepository.get_order_by_payment_intent(db, payment_intent_id)
        if existing_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order already exists for this payment session."
            )

    @staticmethod
    def create_payment_intent(amount: int) -> PaymentIntentResponseSchema:
        """Create a Stripe PaymentIntent"""
        if not stripe.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe API key not configured"
            )

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency="vnd",
                payment_method_types=["card"],
            )
            
            return PaymentIntentResponseSchema(
                payment_intent_id=payment_intent.id,
                client_secret=payment_intent.client_secret,
                amount=amount,
                currency="vnd",
                status=payment_intent.status
            )
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payment intent creation failed: {str(e)}"
            )
    
    @staticmethod
    def confirm_payment_from_cart(db: Session, user_id: int, data: ConfirmPaymentFromCartSchema) -> OrderSchema:
        """Process payment confirmation and create order from user's cart"""
        # 1. Verify payment status on Stripe
        PaymentService._verify_payment_succeeded(data.payment_intent_id)
        
        # 2. Prevent duplicate orders
        PaymentService._check_existing_order(db, data.payment_intent_id)

        try:
            # 3. Create order record
            order_data = CreateOrderFromCartSchema(delivery_address=data.delivery_address)
            order = OrderService.create_order_from_cart(
                db=db,
                user_id=user_id,
                data=order_data,
                payment_intent_id=data.payment_intent_id
            )
            
            # 4. Finalize payment status in database
            OrderRepository.update_payment_status(db, order.id, "completed")
            return OrderService.get_order_by_id(db, order.id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Order processing failed: {str(e)}"
            )
    
    @staticmethod
    def confirm_payment_from_products(db: Session, user_id: int, data: ConfirmPaymentFromProductsSchema) -> OrderSchema:
        """Process payment confirmation and create order for 'Buy Now' flow"""
        # 1. Verify payment status on Stripe
        PaymentService._verify_payment_succeeded(data.payment_intent_id)
        
        # 2. Prevent duplicate orders
        PaymentService._check_existing_order(db, data.payment_intent_id)

        try:
            # 3. Create order record
            order = OrderService.create_order_from_products(
                db=db,
                user_id=user_id,
                items=data.items,
                delivery_address=data.delivery_address.model_dump(),
                payment_intent_id=data.payment_intent_id
            )
            
            # 4. Finalize payment status in database
            OrderRepository.update_payment_status(db, order.id, "completed")
            return OrderService.get_order_by_id(db, order.id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Order processing failed: {str(e)}"
            )

    @staticmethod
    def test_confirm_payment(payment_intent_id: str) -> dict:
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method="pm_card_visa",
            )
            
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
            }

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe confirmation error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Test confirmation failed: {str(e)}"
            )