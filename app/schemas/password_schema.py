from pydantic import BaseModel, EmailStr

class ForgotPasswordOtpSchema(BaseModel):
    email: EmailStr

class ResetPasswordOtpSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class ResetPasswordSchema(BaseModel):
    new_password: str