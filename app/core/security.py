from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import settings
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()

# Use argon2 (Windows-friendly) with bcrypt as fallback
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

RESET_SECRET_KEY = "RESET_SECRET_KEY"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(user_id: int, role_name: str = None) -> str:
    expired = datetime.now() + timedelta(minutes=30)
    payload = {
        "user_id": user_id,
        "role": role_name, 
        "exp": int(expired.timestamp())
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
    return token

def create_reset_token(user_id: str):
    payload = {
        "sub": str(user_id),
        "type": "reset",
        "exp": datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, RESET_SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    return {
        "user_id": payload.get("user_id"),
        "role": payload.get("role")
    }

def require_role(allowed_roles: list[str]):
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
        return current_user
    return role_checker
