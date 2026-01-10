from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base_model import BaseModel


class Order(BaseModel):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationship to user
    user = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    delivery_address = Column(JSON, nullable=False)  # Address object as JSON
    order_date = Column(DateTime, index=True, default=datetime.now)
    total_amount = Column(Float, nullable=False, index=True)
    status = Column(String(50), index=True, default="pending")  # pending, processing, shipped, delivered, cancelled
    payment_status = Column(String(50), index=True, default="pending")  # pending, completed, failed, refunded
    payment_intent_id = Column(String(255), nullable=True, index=True)  # Stripe payment intent ID
    payment_method = Column(String(50), default="stripe")  # stripe, cash_on_delivery
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    

class OrderItem(BaseModel):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    order = relationship("Order", back_populates="items")
    
    product_name = Column(String(255), nullable=False)
    size = Column(Integer, nullable=True)
    color = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)
    


