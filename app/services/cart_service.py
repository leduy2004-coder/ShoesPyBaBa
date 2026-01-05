from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart_schema import (
    AddToCartSchema, 
    CartSchema, 
    CartItemWithProductSchema
)
from app.models.product_model import Product


class CartService:
    """Service for cart business logic"""
    
    @staticmethod
    def get_user_cart(db: Session, user_id: int) -> CartSchema:
        """Get user's cart with all items and product details"""
        cart = CartRepository.get_user_cart(db, user_id)
        cart_items = CartRepository.get_cart_items(db, cart.id)
        
        items_with_products = []
        total_amount = 0
        
        for item in cart_items:
            # Get product details
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                # Use current product price
                current_price = product.price
                subtotal = item.quantity * current_price
                total_amount += subtotal
                
                # Get first image if available
                product_image = None
                if product.image_urls and len(product.image_urls) > 0:
                    if isinstance(product.image_urls, list):
                        product_image = product.image_urls[0].get('url') if isinstance(product.image_urls[0], dict) else product.image_urls[0]
                
                items_with_products.append(
                    CartItemWithProductSchema(
                        id=item.id,
                        product_id=item.product_id,
                        product_name=product.name,
                        product_image=product_image,
                        quantity=item.quantity,
                        size=item.size,
                        color=item.color,
                        current_price=current_price,
                        subtotal=subtotal
                    )
                )
        
        return CartSchema(
            id=cart.id,
            user_id=cart.user_id,
            items=items_with_products,
            total_items=len(items_with_products),
            total_amount=total_amount,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )
    
    @staticmethod
    def add_to_cart(db: Session, user_id: int, data: AddToCartSchema):
        """Add or update (increment) item in cart with validation"""
        # Validate product exists
        product = db.query(Product).filter(Product.id == data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Check if product is active
        if product.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is not available"
            )
        
        # Get or create cart to check existing quantity
        cart = CartRepository.get_user_cart(db, user_id)
        
        # Calculate new quantity to validate stock
        final_quantity = data.quantity
        existing_item = CartRepository.get_cart_item(db, cart.id, data.product_id, data.size, data.color)
        if existing_item:
            final_quantity += existing_item.quantity

        # Validate variant if size/color specified
        if data.size or data.color:
            if not product.variants:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product has no variants"
                )
            
            # check variant exist and have stock
            variant_found = False
            for variant in product.variants:
                if (not data.size or variant.get('size') == data.size) and \
                   (not data.color or variant.get('color') == data.color):
                    if variant.get('stock_quantity', 0) < final_quantity:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Insufficient stock. Available: {variant.get('stock_quantity', 0)}"
                        )
                    variant_found = True
                    break
            
            if not variant_found:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Variant not found"
                )
        
        # Add or update item in cart
        CartRepository.add_item_to_cart(
            db=db,
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity,
            size=data.size,
            color=data.color
        )
        
        return CartService.get_user_cart(db, user_id)
    
    @staticmethod
    def remove_cart_item(db: Session, user_id: int, item_id: int):
        """Remove item from cart"""
        # Verify item belongs to user's cart
        cart = CartRepository.get_user_cart(db, user_id)
        item = CartRepository.get_cart_item_by_id(db, item_id)
        
        if not item or item.cart_id != cart.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        
        CartRepository.remove_cart_item(db, item_id)
        
        return CartService.get_user_cart(db, user_id)
    
    @staticmethod
    def clear_cart(db: Session, user_id: int):
        """Clear all items from cart"""
        cart = CartRepository.get_user_cart(db, user_id)
        CartRepository.clear_cart(db, cart.id)
        
        return {"message": "Cart cleared successfully"}
