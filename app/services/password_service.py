from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_model import User, OTPType
from app.core.security import hash_password
from app.services.email_service import EmailService
from datetime import datetime

class PasswordService:

    @staticmethod
    async def forgot_password_otp(email: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate OTP
        email_service = EmailService()
        otp = email_service.generate_otp()
        otp_expiry = email_service.get_otp_expiry()
        
        # Update user with OTP
        user.otp_code = otp
        user.otp_expired_at = otp_expiry
        user.otp_type = OTPType.RESET
        db.commit()
        
        # Send OTP email
        await email_service.send_otp_email(email, otp, "RESET")
        
        return {"message": "OTP sent to email"}

    @staticmethod
    async def reset_password_with_otp(email: str, otp: str, new_password: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.otp_code != otp or user.otp_type != OTPType.RESET:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        if user.otp_expired_at < datetime.now():
            raise HTTPException(status_code=400, detail="OTP expired")
        
        # Reset password
        user.password = hash_password(new_password)
        user.otp_code = None
        user.otp_expired_at = None
        user.otp_type = None
        db.commit()
        
        return {"message": "Password reset successfully"}
