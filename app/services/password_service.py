from sqlalchemy.orm import Session
from fastapi import HTTPException
from jose import jwt, JWTError
from app.models.user_model import User
from app.core.security import hash_password, create_reset_token, RESET_SECRET_KEY

class PasswordService:

    @staticmethod
    def forgot_password(email: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None

        token = create_reset_token(user.id)
        return token

    @staticmethod
    def reset_password(token: str, new_password: str, db: Session):
        try:
            payload = jwt.decode(token, RESET_SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "reset":
                raise HTTPException(status_code=400, detail="Invalid token")

            user_id = payload.get("sub")

        except JWTError:
            raise HTTPException(status_code=400, detail="Token expired or invalid")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password = hash_password(new_password)
        db.commit()
