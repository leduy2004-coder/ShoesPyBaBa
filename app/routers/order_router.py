from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from datetime import datetime
from app.db.base import get_db
from app.services.order_service import OrderService
from app.schemas.order_schema import (
    OrderSchema,
    OrderSearchSchema,
    OrderHistorySchema,
    UpdateOrderSchema
)
from app.core.security import get_current_user

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.get("", response_model=OrderHistorySchema)
async def get_user_orders(
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get current user's order history"""
    return OrderService.get_user_orders(db, current_user["user_id"], page, limit)


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Get order details"""
    order = OrderService.get_order_by_id(db, order_id)
    
    # Verify order belongs to current user (unless admin)
    if order.user_id != current_user["user_id"] and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return order


@router.get("/search/all", response_model=OrderHistorySchema)
async def search_orders(
    current_user: Annotated[dict, Depends(get_current_user)],
    status_filter: Optional[str] = Query(None, alias="status"),
    payment_status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search user's orders with filters"""
    filters = OrderSearchSchema(
        user_id=current_user["user_id"],
        status=status_filter,
        payment_status=payment_status,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )
    
    return OrderService.search_orders(db, filters)


# Admin endpoints
@router.get("/admin/by-user/{user_id}", response_model=OrderHistorySchema)
async def get_orders_by_user(
    user_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Admin: Get all orders by specific user"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return OrderService.get_user_orders(db, user_id, page, limit)


@router.get("/admin/by-product/{product_id}", response_model=OrderHistorySchema)
async def get_orders_by_product(
    product_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Admin: Get all orders containing specific product"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return OrderService.get_orders_by_product(db, product_id, page, limit)


@router.put("/admin/{order_id}/status", response_model=OrderSchema)
async def update_order_status(
    order_id: int,
    data: UpdateOrderSchema,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Admin: Update order status"""
    # Check if current user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if data.status:
        return OrderService.update_order_status(db, order_id, data.status)
    
    return OrderService.get_order_by_id(db, order_id)
