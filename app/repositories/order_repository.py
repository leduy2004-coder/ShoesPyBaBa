from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.order_model import Order, OrderItem
from app.models.cart_model import CartItem
import math


class OrderRepository:
    """Repository for order operations"""
    
    @staticmethod
    def create_order(db: Session, user_id: int, delivery_address: Dict[str, Any], 
                    total_amount: float, payment_method: str = "stripe",
                    payment_intent_id: Optional[str] = None) -> Order:
        """Create new order"""
        order = Order(
            user_id=user_id,
            delivery_address=delivery_address,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_intent_id=payment_intent_id,
            status="pending",
            payment_status="pending"
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def create_order_items(db: Session, order_id: int, cart_items: List[CartItem]) -> List[OrderItem]:
        """Create order items from cart items"""
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order_id,
                product_id=cart_item.product_id,
                product_name="",  # Will be filled by service
                size=cart_item.size,
                color=cart_item.color,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.price_snapshot
            )
            order_items.append(order_item)
        
        db.add_all(order_items)
        db.commit()
        return order_items
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_order_items(db: Session, order_id: int) -> List[OrderItem]:
        """Get all items for an order"""
        return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    @staticmethod
    def get_user_orders(db: Session, user_id: int, page: int = 1, limit: int = 10) -> tuple[List[Order], int]:
        """Get user's order history with pagination"""
        query = db.query(Order).filter(Order.user_id == user_id).order_by(desc(Order.created_at))
        
        total = query.count()
        orders = query.offset((page - 1) * limit).limit(limit).all()
        
        return orders, total
    
    @staticmethod
    def update_order_status(db: Session, order_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        order = OrderRepository.get_order_by_id(db, order_id)
        if order:
            order.status = status
            db.commit()
            db.refresh(order)
        return order
    
    @staticmethod
    def update_payment_status(db: Session, order_id: int, payment_status: str) -> Optional[Order]:
        """Update payment status"""
        order = OrderRepository.get_order_by_id(db, order_id)
        if order:
            order.payment_status = payment_status
            if payment_status == "completed":
                order.status = "processing"  # Move to processing when payment is completed
            db.commit()
            db.refresh(order)
        return order
    
    @staticmethod
    def search_orders(db: Session, user_id: Optional[int] = None, status: Optional[str] = None,
                     payment_status: Optional[str] = None, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None, page: int = 1, limit: int = 10) -> tuple[List[Order], int]:
        """Search orders with filters"""
        query = db.query(Order)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        if status:
            query = query.filter(Order.status == status)
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        query = query.order_by(desc(Order.created_at))
        
        total = query.count()
        orders = query.offset((page - 1) * limit).limit(limit).all()
        
        return orders, total
    
    @staticmethod
    def get_orders_by_product(db: Session, product_id: int, page: int = 1, limit: int = 10) -> tuple[List[Order], int]:
        """Admin: Get all orders containing a specific product"""
        query = db.query(Order).join(OrderItem).filter(OrderItem.product_id == product_id).order_by(desc(Order.created_at))
        
        total = query.count()
        orders = query.offset((page - 1) * limit).limit(limit).all()
        
        return orders, total
    
    @staticmethod
    def get_order_by_payment_intent(db: Session, payment_intent_id: str) -> Optional[Order]:
        """Get order by Stripe payment intent ID"""
        return db.query(Order).filter(Order.payment_intent_id == payment_intent_id).first()
