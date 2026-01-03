from sqlalchemy.orm import Session
from app.models.user_model import User
from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.schemas.user_schemas import LoginUserResponseSchema, UserProfileUpdate, UserProfileResponse
from app.repositories.address_repository import AddressRepository
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository

class UserService:
    @staticmethod
    async def google_login(code: str, db: Session) -> LoginUserResponseSchema:
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            # Get access token
            token_response = await client.post(settings.GOOGLE_TOKEN_ENDPOINT, data=data)
            token_data = token_response.json()
            
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to retrieve access token")
            
            # Get user info
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = await client.get(settings.GOOGLE_USERINFO_ENDPOINT, headers=headers)
            userinfo = userinfo_response.json()
            
            email = userinfo.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in Google account")

            user_repo = UserRepository(db)
            
            # Check if user exists
            user = user_repo.get_by_email(email)
            
            if not user:
                # Create new user
                user = User(
                    full_name=userinfo.get("name"),
                    email=email,
                    avatar=userinfo.get("picture"),
                    password=hash_password("google_oauth_user"), # Placeholder password
                    role_id=2, # Default to user role
                    status=1,
                    gender="Other"
                )
                user = user_repo.create(user)
            else:
                # Update avatar if changed
                if userinfo.get("picture") and user.avatar != userinfo.get("picture"):
                    user.avatar = userinfo.get("picture")
                    user_repo.update()
                    db.refresh(user)

            # Create access token for our system
            token = create_access_token(user.id)
            
            return LoginUserResponseSchema(access_token=token, token_type="Bearer")

    @staticmethod
    async def get_google_profile(access_token: str):
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            try:
                userinfo_response = await client.get(settings.GOOGLE_USERINFO_ENDPOINT, headers=headers)
                userinfo_response.raise_for_status()
                return userinfo_response.json()
            except httpx.HTTPStatusError:
                raise HTTPException(status_code=401, detail="Invalid or expired access token")

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
        
        
