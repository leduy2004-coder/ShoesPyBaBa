from pydantic import BaseModel, EmailStr, Field

class ForgotPasswordOtpSchema(BaseModel):
    email: EmailStr

class ResetPasswordOtpSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class ChangePasswordSchema(BaseModel):
    old_password: str = Field(..., description="Mật khẩu hiện tại")
    new_password: str = Field(..., min_length=6, description="Mật khẩu mới")
    confirm_password: str = Field(..., description="Xác nhận mật khẩu mới")