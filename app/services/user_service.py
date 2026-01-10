from sqlalchemy.orm import Session
from app.models.user_model import User, OTPType
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.schemas.user_schemas import LoginUserResponseSchema, UserProfileUpdate, UserProfileResponse
from app.repositories.address_repository import AddressRepository
from app.models.address_model import Address
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
        self.address_repository = AddressRepository(db)

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
    


    def update_user_profile(self, user: User, data: UserProfileUpdate):

        if data.email != user.email:
            email_exists = self.db.query(User).filter(
                User.email == data.email,
                User.id != user.id
            ).first()
            
            if email_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use."
                )
    
            user.email = data.email

        user.full_name = data.full_name
        user.phone_number = data.phone_number

        address = self.db.query(Address).filter(
            Address.user_id == user.id, 
            Address.is_default == True
        ).first()

        if address:
            address.province_city = data.province_city
            address.ward = data.ward
            address.street_address = data.street_address
            address.recipient_name = data.full_name
            address.recipient_phone = data.phone_number
        else:
            new_address = Address(
                user_id=user.id,
                province_city=data.province_city,
                ward=data.ward,
                street_address=data.street_address,
                recipient_name=data.full_name,   
                recipient_phone=data.phone_number,
                is_default=True
            )
            self.db.add(new_address)
            address = new_address
        
        self.db.commit()
        self.db.refresh(user)

        if address.id:
            self.db.refresh(address)

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone_number=user.phone_number,
            province_city=address.province_city,
            ward=address.ward,
            street_address=address.street_address
        )
        