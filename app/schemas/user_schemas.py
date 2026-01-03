from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator
from typing import Optional
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
    phone_number: Optional[str]
    street_address: Optional[str] = None
    ward: Optional[str] = None
    province_city: Optional[str] = None
    
    class Config:
        from_attributes = True
