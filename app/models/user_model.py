from app.models.base_model import BaseModel
from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey, Boolean
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Enum
import enum

class OTPType(enum.Enum):
    REGISTER = "REGISTER"
    RESET = "RESET"


class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), index=True)  
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255), index=True)
    gender = Column(String(20), nullable=True)  
    avatar = Column(String(500), nullable=True)
    phone_number = Column(String(20), nullable=True, index=True) 
    role_id = Column(Integer, ForeignKey("role.id"), nullable=True)

    # 0 = chưa xác thực | 1 = đã xác thực
    status = Column(Integer, index=True, default=0)

    # 👉 OTP
    otp_code = Column(String(255), nullable=True)
    otp_expired_at = Column(DateTime, nullable=True)
    otp_type = Column(Enum(OTPType), nullable=True)

    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime, index=True, default=datetime.now)





def seed_admin(db: Session):
    """Create default admin user if not exists"""
    from app.core.security import hash_password 
    
    existing_admin = db.query(User).filter(User.email == "admin@yopmail.com").first()
    
    if not existing_admin:
        admin = User(
            full_name="Admin",
            email="admin@yopmail.com",
            password=hash_password("admin"),
            role_id=1,  # admin role
            status=True
        )
        db.add(admin)
        db.commit()
        print("✓ Admin user created: admin@example.com / admin123")
    else:
        print("✓ Admin user already exists, skipping seed.")
