
import jwt
from app.core import security
from app.core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials 
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.schemas.user_schemas import TokenPayload
from app.models.user_model import User

def authenticate(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)

    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    user = (
        db.query(User)
        .filter(User.id == token_data.user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user