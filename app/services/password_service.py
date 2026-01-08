from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user_model import User, OTPType
from app.core.security import hash_password, verify_password
from app.services.email_service import EmailService
from datetime import datetime, timedelta

class PasswordService:

    @staticmethod
    async def forgot_password_otp(email: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        now = datetime.now()

        # ⛔ Check resend OTP (1 phút)
        if user.otp_sent_at:
            resend_time = user.otp_sent_at + timedelta(minutes=1)
            if now < resend_time:
                remain = int((resend_time - now).total_seconds())
                raise HTTPException(
                    status_code=429,
                    detail=f"Please wait {remain}s before resending OTP"
                )

        email_service = EmailService()
        otp = email_service.generate_otp()
        otp_expiry = now + timedelta(minutes=3)

        user.otp_code = otp
        user.otp_expired_at = otp_expiry
        user.otp_sent_at = now
        user.otp_type = OTPType.RESET

        db.commit()

        # ✅ await HỢP LỆ vì đang ở async def
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
    
    @staticmethod
    async def change_password(current_user, data, db):
        if not verify_password(data.old_password, current_user.password):
            raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác")
        
        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Mật khẩu mới và xác nhận mật khẩu không khớp")
        
        current_user.password = hash_password(data.new_password)
        db.commit()
        db.refresh(current_user)
        
        return True
