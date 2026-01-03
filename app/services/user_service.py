from sqlalchemy.orm import Session
from app.models.user_model import User, OTPType
from app.core.config import settings
from app.schemas.user_schemas import TokenPayload
from fastapi import HTTPException, Depends
import jwt
from pydantic import ValidationError
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from datetime import datetime

class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db

    def get_profile(self, token: str) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY,
                algorithms=settings.ALGORITHM
            )
            token_data = TokenPayload(**payload)
        except (jwt.PyJWTError, ValidationError):
             raise HTTPException(
                status_code=403,
                detail="credentials"
            )
        
        user = self.user_repo.get_by_id(token_data.user_id)
        if not user:
             raise HTTPException(status_code=404, detail="User not found")
        
        async with httpx.AsyncClient() as client:
            try:
                token_response = await client.post(settings.GOOGLE_TOKEN_ENDPOINT, data=data)
                token_response.raise_for_status()
                return token_response.json()
            except httpx.HTTPStatusError:
                raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    @staticmethod
    async def register_with_otp(data, db: Session):
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate OTP
        email_service = EmailService()
        otp = email_service.generate_otp()
        otp_expiry = email_service.get_otp_expiry()
        
        # Create user with OTP
        password = hash_password(data.password)
        user = User(
            full_name=data.full_name, 
            email=data.email, 
            password=password, 
            gender=data.gender, 
            phone_number=data.phone_number,
            status=0,  # Not verified
            otp_code=otp,
            otp_expired_at=otp_expiry,
            otp_type=OTPType.REGISTER
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Send OTP email
        await email_service.send_otp_email(data.email, otp, "REGISTER")
        
        return user

    @staticmethod
    async def verify_otp(email: str, otp: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.otp_code != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        if user.otp_expired_at < datetime.now():
            raise HTTPException(status_code=400, detail="OTP expired")
        
        # Verify user
        user.status = 1
        user.otp_code = None
        user.otp_expired_at = None
        user.otp_type = None
        db.commit()
        
        return user
