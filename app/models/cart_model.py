from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from datetime import datetime
from app.models.base_model import BaseModel


class Cart(BaseModel):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class CartItem(BaseModel):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    size = Column(Integer, nullable=True)
    color = Column(String(50), nullable=True)
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True, default=datetime.now, onupdate=datetime.now)
