from sqlalchemy import Column, String, Boolean, Integer, ForeignKey

from app.models.base_model import BaseModel


class Address(BaseModel):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    street_address = Column(String(255), nullable=False)
    ward = Column(String(100), nullable=True)
    province_city = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False, index=True)
    recipient_name = Column(String(100), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    


