from fastapi import APIRouter
from app.schemas.user_schemas import UserSchema
from app.models.user_model import User
from app.db.base import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.schemas.base_schema import DataResponse
from app.core.security import security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.user_service import UserService

router = APIRouter()

@router.get("/profile", tags=["users"], description="Get current user", response_model=DataResponse[UserSchema])
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user_service = UserService(db)
    current_user = user_service.get_profile(credentials)
    return DataResponse.custom_response(code="200", message="Get current user success", data=current_user)



