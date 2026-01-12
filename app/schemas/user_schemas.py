from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator
from typing import Optional
from enum import Enum
import re

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    full_name: str
    email: str
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    role_id: Optional[int] = None
    status: int

class RegisterUserSchema(BaseModel):
    full_name: str
    email: str
    password: str
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, email: str):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Invalid email address')
        return email

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str):
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return password

class LoginUserSchema(BaseModel):
    email: str
    password: str
    
class LoginUserResponseSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    role: Optional[str] = None

class LoginUserByGoogleResponseSchema(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    role: Optional[str] = None
    google_refresh_token: str

class TokenPayload(BaseModel):
    user_id: int
    exp: int

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    street_address: Optional[str] = None
    ward: Optional[str] = None
    province_city: Optional[str] = None

class UserProfileResponse(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None  # Thêm = None ở đây
    street_address: Optional[str] = None
    ward: Optional[str] = None
    province_city: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True) # Cách viết mới cho Pydantic v2

class VerifyOtpSchema(BaseModel):
    email: str
    otp: str

class ForgotPasswordOtpSchema(BaseModel):
    email: str

class ResetPasswordOtpSchema(BaseModel):
    email: str
    otp: str
    new_password: str

class OTPType(str, Enum):
    # Member (Tên) = "Value" (Giá trị thực tế trong DB/Request)
    REGISTER = "REGISTER"
    RESET = "RESET"

