from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from app.models.cart_model import Cart, CartItem
from app.models.product_model import Product
from sqlalchemy import and_, or_

class CartRepository:
    """Repository for cart operations"""
    
    @staticmethod
    def get_user_cart(db: Session, user_id: int) -> Optional[Cart]:
        """Get user's cart, create if doesn't exist"""
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart
    
    @staticmethod
    def get_cart_items(db: Session, cart_id: int) -> List[CartItem]:
        """Get all items in cart"""
        return db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    
    @staticmethod
    def get_cart_item(
        db: Session,
        cart_id: int,
        product_id: int,
        size: Optional[int] = None,
        color: Optional[str] = None
    ) -> Optional[CartItem]:
        query = db.query(CartItem).filter(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
            or_(CartItem.size == size, and_(CartItem.size.is_(None), size is None)),
            or_(CartItem.color == color, and_(CartItem.color.is_(None), color is None))
        )
        
        return query.first()

    
    @staticmethod
    def get_cart_item_by_id(db: Session, item_id: int) -> Optional[CartItem]:
        """Get cart item by ID"""
        return db.query(CartItem).filter(CartItem.id == item_id).first()
    
    @staticmethod
    def add_item_to_cart(db: Session, cart_id: int, product_id: int, quantity: int, 
                        size: Optional[int], color: Optional[str]) -> CartItem:
        """Add item to cart or increment quantity if it exists."""
        existing_item = CartRepository.get_cart_item(db, cart_id, product_id, size, color)
        
        if existing_item:
            existing_item.quantity += quantity
            
            if existing_item.quantity <= 0:
                db.delete(existing_item)
                db.commit()
                return None
                
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            if quantity <= 0:
                return None
                
            new_item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity,
                size=size,
                color=color
            )
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            return new_item
    
    @staticmethod
    def remove_cart_item(db: Session, item_id: int) -> bool:
        """Remove item from cart"""
        item = CartRepository.get_cart_item_by_id(db, item_id)
        if item:
            db.delete(item)
            db.commit()
            return True
        return False
    
    @staticmethod
    def clear_cart(db: Session, cart_id: int) -> bool:
        """Clear all items from cart"""
        db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        db.commit()
        return True
    
    @staticmethod
    def get_cart_total(db: Session, cart_id: int) -> float:
        """Calculate total amount for cart using current product prices"""
        items = CartRepository.get_cart_items(db, cart_id)
        total = 0
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                total += item.quantity * product.price
        return total
