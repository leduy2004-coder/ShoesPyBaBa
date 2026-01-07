from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated
from app.db.base import get_db
from app.services.cart_service import CartService
from app.schemas.cart_schema import (
    AddToCartSchema,
    CartSchema
)
from app.core.security import get_current_user

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("", response_model=CartSchema)
async def get_cart(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get current user's cart"""
    return CartService.get_user_cart(db, current_user["user_id"])


@router.post("/items", response_model=CartSchema, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    data: AddToCartSchema,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Add or update (increment) item in cart"""
    return CartService.add_to_cart(db, current_user["user_id"], data)


@router.delete("/items/{item_id}", response_model=CartSchema)
async def remove_cart_item(
    item_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    return CartService.remove_cart_item(db, current_user["user_id"], item_id)


@router.delete("")
async def clear_cart(
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Clear entire cart"""
    return CartService.clear_cart(db, current_user["user_id"])
