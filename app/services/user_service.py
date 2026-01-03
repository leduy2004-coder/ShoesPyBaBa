from sqlalchemy.orm import Session
from app.models.user_model import User
from app.core.config import settings
from app.schemas.user_schemas import TokenPayload
from fastapi import HTTPException, Depends
import jwt
from pydantic import ValidationError
from app.repositories.user_repository import UserRepository

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
        
        return user
