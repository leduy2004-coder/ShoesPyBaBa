from sqlalchemy.orm import Session
from app.models.user_model import User, OTPType
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.schemas.user_schemas import LoginUserResponseSchema, UserProfileUpdate, UserProfileResponse
from app.repositories.address_repository import AddressRepository
from fastapi import HTTPException
from app.schemas.user_schemas import TokenPayload
from fastapi import HTTPException, Depends
import jwt
from pydantic import ValidationError
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService
from datetime import datetime

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


    @staticmethod
    async def refresh_google_token(refresh_token: str):
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")
        
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                token_response = await client.post(settings.GOOGLE_TOKEN_ENDPOINT, data=data)
                token_response.raise_for_status()
                return token_response.json()
            except httpx.HTTPStatusError:
                raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    def __init__(self, db: Session):
        self.db = db
        self.address_repository = AddressRepository(db)

    def update_user_profile(self, current_user: User, data: UserProfileUpdate):

        current_user.full_name = data.full_name
        current_user.email = data.email
        current_user.phone_number = data.phone_number

        address = self.address_repository.get_default_address(current_user.id)

        if address:
            address.street_address = data.street_address
            address.ward = data.ward
            address.province_city = data.province_city
            address.recipient_name = current_user.full_name
            address.recipient_email = current_user.email
            address.recipient_phone = current_user.phone_number
        else:
            address_data = {
                "street_address": data.street_address,
                "ward": data.ward,
                "province_city": data.province_city,
                "recipient_name": current_user.full_name,
                "recipient_email": current_user.email,
                "recipient_phone": current_user.phone_number
            }
            self.address_repository.creata_default_address(current_user.id, address_data)
        
        self.db.commit()
        self.db.refresh(current_user)

        update_address = self.address_repository.get_default_address(current_user.id)

        return UserProfileResponse(
            user_id=current_user.id,
            full_name=current_user.full_name,
            email=current_user.email,
            phone_number=current_user.phone_number,
            street_address=update_address.street_address if update_address else None,
            ward=update_address.ward if update_address else None,
            province_city=update_address.province_city if update_address else None 
        )
        
