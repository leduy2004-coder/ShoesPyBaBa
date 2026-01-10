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

# Initialize load_dotenv
load_dotenv()

# Get Stripe key from environment
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")

# Initialize Stripe only if a valid key is provided
if STRIPE_KEY and STRIPE_KEY != "mock" and STRIPE_KEY != "sk_test_your_secret_key_here":
    stripe.api_key = STRIPE_KEY
else:
    stripe.api_key = None

class PaymentService:
    @staticmethod
    def _is_mock_mode(payment_intent_id: Optional[str] = None) -> bool:
        """Helper to determine if we should run in mock mode"""
        if not stripe.api_key:
            return True
        if payment_intent_id and payment_intent_id.startswith("pi_mock_"):
            return True
        return False

    @staticmethod
    def create_payment_intent(amount: int) -> PaymentIntentResponseSchema:
        """Create Stripe payment intent (Supports Mock mode for testing)"""
        if PaymentService._is_mock_mode():
            return PaymentIntentResponseSchema(
                payment_intent_id=f"pi_mock_{os.urandom(8).hex()}",
                client_secret="mock_secret_for_testing_only",
                amount=amount,
                currency="usd",
                status="succeeded"
            )

        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_in_cents = int(amount * 100)
            
            # Create payment intent with card only
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency="usd",
                payment_method_types=["card"],
            )
            
            return PaymentIntentResponseSchema(
                payment_intent_id=payment_intent.id,
                client_secret=payment_intent.client_secret,
                amount=amount,
                currency="usd",
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
        """Confirm payment and create order from cart"""
        try:
            # MOCK MODE check
            if not PaymentService._is_mock_mode(data.payment_intent_id):
                # Retrieve payment intent from Stripe
                payment_intent = stripe.PaymentIntent.retrieve(data.payment_intent_id)
                
                # Check payment status
                if payment_intent.status != "succeeded":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Payment not completed. Status: {payment_intent.status}"
                    )
            
            # Check if order already exists for this payment intent
            existing_order = OrderRepository.get_order_by_payment_intent(db, data.payment_intent_id)
            if existing_order:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order already created for this payment"
                )
            
            # Create order from cart
            order_data = CreateOrderFromCartSchema(
                delivery_address=data.delivery_address
            )
            
            order = OrderService.create_order_from_cart(
                db=db,
                user_id=user_id,
                data=order_data,
                payment_intent_id=data.payment_intent_id
            )
            
            # Update payment status to completed
            OrderRepository.update_payment_status(db, order.id, "completed")
            
            # Refresh order data
            return OrderService.get_order_by_id(db, order.id)
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Order creation failed: {str(e)}"
            )
    
    @staticmethod
    def confirm_payment_from_products(db: Session, user_id: int, data: ConfirmPaymentFromProductsSchema) -> OrderSchema:
        """Confirm payment and create order from products (buy now)"""
        try:
            # MOCK MODE check
            if not PaymentService._is_mock_mode(data.payment_intent_id):
                # Retrieve payment intent from Stripe
                payment_intent = stripe.PaymentIntent.retrieve(data.payment_intent_id)
                
                # Check payment status
                if payment_intent.status != "succeeded":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Payment not completed. Status: {payment_intent.status}"
                    )
            
            # Check if order already exists for this payment intent
            existing_order = OrderRepository.get_order_by_payment_intent(db, data.payment_intent_id)
            if existing_order:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order already created for this payment"
                )
            
            # Create order from products
            order = OrderService.create_order_from_products(
                db=db,
                user_id=user_id,
                items=data.items,
                delivery_address=data.delivery_address.model_dump(),
                payment_intent_id=data.payment_intent_id
            )
            
            # Update payment status to completed
            OrderRepository.update_payment_status(db, order.id, "completed")
            
            # Refresh order data
            return OrderService.get_order_by_id(db, order.id)
            
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Order creation failed: {str(e)}"
            )


    @staticmethod
    def test_confirm_payment(payment_intent_id: str) -> dict:
        """TEST ONLY: Automatically confirm payment on Stripe using test card method"""
        try:
            # MOCK MODE check
            if PaymentService._is_mock_mode(payment_intent_id):
                return {
                    "payment_intent_id": payment_intent_id,
                    "status": "succeeded",
                    "amount": 0, # In mock mode amount doesn't matter for confirmation
                    "currency": "usd",
                    "message": "MOCK MODE: Payment auto-confirmed as success."
                }

            # 1. Confirm payment intent with test card
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method="pm_card_visa",
            )
            
            return {
                "payment_intent_id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount / 100,
                "currency": payment_intent.currency,
                "message": "Payment confirmed successfully on Stripe (Test Card)."
            }

        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Test confirmation failed: {str(e)}"
            )