from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import settings
import jwt

# Use argon2 (Windows-friendly) with bcrypt as fallback
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

RESET_SECRET_KEY = "RESET_SECRET_KEY"
RESET_TOKEN_EXPIRE_MINUTES = 15

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_access_token(user_id: int) -> str:
    expired = datetime.now() + timedelta(minutes=30)
    payload = {
        "user_id": user_id,
        "exp": int(expired.timestamp())
    }
    
    token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
    return token

def create_reset_token(user_id: str):
    payload = {
        "sub": str(user_id),
        "type": "reset",
        "exp": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, RESET_SECRET_KEY, algorithm="HS256")
