from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order_schema import (
    CreateOrderFromCartSchema,
    DirectOrderItemSchema,
    OrderSchema,
    OrderSearchSchema,
    OrderHistorySchema
)
from app.models.product_model import Product
import math


class OrderService:
    """Service for order business logic"""
    
    @staticmethod
    def create_order_from_cart(db: Session, user_id: int, data: CreateOrderFromCartSchema, 
                              payment_intent_id: Optional[str] = None) -> OrderSchema:
        """Create order from user's cart"""
        # Get user's cart
        cart = CartRepository.get_user_cart(db, user_id)
        cart_items = CartRepository.get_cart_items(db, cart.id)
        
        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        
        # Calculate total using current product prices
        total_amount = 0
        for cart_item in cart_items:
            product = db.query(Product).filter(Product.id == cart_item.product_id).first()
            if product:
                total_amount += cart_item.quantity * product.price
        
        # Create order (always use stripe payment)
        order = OrderRepository.create_order(
            db=db,
            user_id=user_id,
            delivery_address=data.delivery_address.model_dump(),
            total_amount=total_amount,
            payment_method="stripe",
            payment_intent_id=payment_intent_id
        )
        
        # Create order items with product names and current prices
        for cart_item in cart_items:
            product = db.query(Product).filter(Product.id == cart_item.product_id).first()
            if product:
                from app.models.order_model import OrderItem
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    product_name=product.name,
                    size=cart_item.size,
                    color=cart_item.color,
                    quantity=cart_item.quantity,
                    price_at_purchase=product.price  # Use current price at time of order
                )
                db.add(order_item)
                
                # Decrement stock
                ProductRepository.decrement_stock(
                    db=db,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    size=cart_item.size,
                    color=cart_item.color
                )
        
        db.commit()
        
        # Clear cart after order creation
        CartRepository.clear_cart(db, cart.id)
        
        # Return order with items
        return OrderService.get_order_by_id(db, order.id)
    
    @staticmethod
    def create_order_from_products(
        db: Session, 
        user_id: int, 
        items: List[DirectOrderItemSchema],
        delivery_address: dict,
        payment_intent_id: str
    ) -> OrderSchema:
        """Create order directly from product list (buy now)"""
        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No items provided"
            )
        
        # Validate products and calculate total
        total_amount = 0
        validated_items = []
        
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item.product_id} not found"
                )
            
            if product.status != "active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {product.name} is not available"
                )
            
            # Validate variant if size/color specified
            if item.size or item.color:
                if not product.variants:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Product {product.name} has no variants"
                    )
                
                variant_found = False
                for variant in product.variants:
                    if (not item.size or variant.get('size') == item.size) and \
                       (not item.color or variant.get('color') == item.color):
                        if variant.get('stock_quantity', 0) < item.quantity:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Insufficient stock for {product.name}"
                            )
                        variant_found = True
                        break
                
                if not variant_found:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Variant not found for {product.name}"
                    )
            
            total_amount += item.quantity * product.price
            validated_items.append((item, product))
        
        # Create order (always use stripe payment)
        order = OrderRepository.create_order(
            db=db,
            user_id=user_id,
            delivery_address=delivery_address,
            total_amount=total_amount,
            payment_method="stripe",
            payment_intent_id=payment_intent_id
        )
        
        # Create order items
        for item, product in validated_items:
            from app.models.order_model import OrderItem
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=product.name,
                size=item.size,
                color=item.color,
                quantity=item.quantity,
                price_at_purchase=product.price
            )
            db.add(order_item)
            
            # Decrement stock
            ProductRepository.decrement_stock(
                db=db,
                product_id=item.product_id,
                quantity=item.quantity,
                size=item.size,
                color=item.color
            )
        
        db.commit()
        
        # Return order with items
        return OrderService.get_order_by_id(db, order.id)
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> OrderSchema:
        """Get order with items"""
        order = OrderRepository.get_order_by_id(db, order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        items = OrderRepository.get_order_items(db, order_id)
        
        return OrderSchema(
            id=order.id,
            user_id=order.user_id,
            delivery_address=order.delivery_address,
            order_date=order.order_date,
            total_amount=order.total_amount,
            status=order.status,
            payment_status=order.payment_status,
            payment_intent_id=order.payment_intent_id,
            payment_method=order.payment_method,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[{
                "id": item.id,
                "order_id": item.order_id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "size": item.size,
                "color": item.color,
                "quantity": item.quantity,
                "price_at_purchase": item.price_at_purchase
            } for item in items]
        )
    
    @staticmethod
    def get_user_orders(db: Session, user_id: int, page: int = 1, limit: int = 10) -> OrderHistorySchema:
        """Get user's order history"""
        orders, total = OrderRepository.get_user_orders(db, user_id, page, limit)
        
        order_schemas = []
        for order in orders:
            items = OrderRepository.get_order_items(db, order.id)
            order_schemas.append(OrderSchema(
                id=order.id,
                user_id=order.user_id,
                delivery_address=order.delivery_address,
                order_date=order.order_date,
                total_amount=order.total_amount,
                status=order.status,
                payment_status=order.payment_status,
                payment_intent_id=order.payment_intent_id,
                payment_method=order.payment_method,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[{
                    "id": item.id,
                    "order_id": item.order_id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "size": item.size,
                    "color": item.color,
                    "quantity": item.quantity,
                    "price_at_purchase": item.price_at_purchase
                } for item in items]
            ))
        
        total_pages = math.ceil(total / limit) if total > 0 else 0
        
        return OrderHistorySchema(
            orders=order_schemas,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    @staticmethod
    def search_orders(db: Session, filters: OrderSearchSchema) -> OrderHistorySchema:
        """Search orders with filters"""
        orders, total = OrderRepository.search_orders(
            db=db,
            user_id=filters.user_id,
            status=filters.status,
            payment_status=filters.payment_status,
            start_date=filters.start_date,
            end_date=filters.end_date,
            page=filters.page,
            limit=filters.limit
        )
        
        order_schemas = []
        for order in orders:
            items = OrderRepository.get_order_items(db, order.id)
            order_schemas.append(OrderSchema(
                id=order.id,
                user_id=order.user_id,
                delivery_address=order.delivery_address,
                order_date=order.order_date,
                total_amount=order.total_amount,
                status=order.status,
                payment_status=order.payment_status,
                payment_intent_id=order.payment_intent_id,
                payment_method=order.payment_method,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[{
                    "id": item.id,
                    "order_id": item.order_id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "size": item.size,
                    "color": item.color,
                    "quantity": item.quantity,
                    "price_at_purchase": item.price_at_purchase
                } for item in items]
            ))
        
        total_pages = math.ceil(total / filters.limit) if total > 0 else 0
        
        return OrderHistorySchema(
            orders=order_schemas,
            total=total,
            page=filters.page,
            limit=filters.limit,
            total_pages=total_pages
        )
    
    @staticmethod
    def get_orders_by_product(db: Session, product_id: int, page: int = 1, limit: int = 10) -> OrderHistorySchema:
        """Admin: Get orders by product"""
        orders, total = OrderRepository.get_orders_by_product(db, product_id, page, limit)
        
        order_schemas = []
        for order in orders:
            items = OrderRepository.get_order_items(db, order.id)
            order_schemas.append(OrderSchema(
                id=order.id,
                user_id=order.user_id,
                delivery_address=order.delivery_address,
                order_date=order.order_date,
                total_amount=order.total_amount,
                status=order.status,
                payment_status=order.payment_status,
                payment_intent_id=order.payment_intent_id,
                payment_method=order.payment_method,
                created_at=order.created_at,
                updated_at=order.updated_at,
                items=[{
                    "id": item.id,
                    "order_id": item.order_id,
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "size": item.size,
                    "color": item.color,
                    "quantity": item.quantity,
                    "price_at_purchase": item.price_at_purchase
                } for item in items]
            ))
        
        total_pages = math.ceil(total / limit) if total > 0 else 0
        
        return OrderHistorySchema(
            orders=order_schemas,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    
    @staticmethod
    def update_order_status(db: Session, order_id: int, status: str) -> OrderSchema:
        """Admin: Update order status"""
        order = OrderRepository.update_order_status(db, order_id, status)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        return OrderService.get_order_by_id(db, order_id)
