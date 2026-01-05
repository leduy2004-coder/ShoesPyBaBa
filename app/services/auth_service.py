from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schemas import RegisterUserSchema, LoginUserResponseSchema, LoginUserSchema
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from fastapi import HTTPException
import httpx
from app.repositories.user_repository import UserRepository 
from app.core.config import logger
from datetime import datetime, timedelta, timezone
from app.services.email_service import EmailService


from app.repositories.role_repository import RoleRepository
from app.services.role_service import RoleService

class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.role_service = RoleService(db)
        self.db = db

    def register_user(self, data: RegisterUserSchema) -> User:
        password = hash_password(data.password)
        user = User(
            full_name=data.full_name,
            email=data.email,
            password=password,
            gender=data.gender,
            phone_number=data.phone_number,
            status=0
        )
        return self.user_repo.create_user(user)

    def login_user(self, data: LoginUserSchema) -> LoginUserResponseSchema:
   
        user = self.user_repo.get_by_email(data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
    
        if not verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        logger.info("Login attempt with email=%s", user.role_id)

        role_name = self.role_service.get_role_name_by_id(user.role_id) if user.role_id else "user"
        logger.info("Role name: %s", role_name)
        token = create_access_token(user.id, role_name)

        return LoginUserResponseSchema(
            access_token=token, 
            token_type="Bearer",
            role=role_name
        )

    async def google_login(self, code: str) -> LoginUserResponseSchema:
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(settings.GOOGLE_TOKEN_ENDPOINT, data=data)
            token_data = token_response.json()
            
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to retrieve access token")
            
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = await client.get(settings.GOOGLE_USERINFO_ENDPOINT, headers=headers)
            userinfo = userinfo_response.json()
            
            email = userinfo.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in Google account")

            # Check if user exists
            user = self.user_repo.get_by_email(email)
            
            if not user:
                # Create new user
                user = User(
                    full_name=userinfo.get("name"),
                    email=email,
                    avatar=userinfo.get("picture"),
                    password=hash_password("google_oauth_user"), 
                    role_id=2, 
                    status=1,
                    gender="Other"
                )
                user = self.user_repo.create_user(user)
            else:
                # Update avatar if changed - logic kept from UserService
                 if userinfo.get("picture") and user.avatar != userinfo.get("picture"):
                    user.avatar = userinfo.get("picture")
                    self.db.commit() # AuthRepo doesn't have update method yet, using db directly or add update to repo
                    self.db.refresh(user)

            role_name = self.role_service.get_role_name_by_id(user.role_id) if user.role_id else "user"
            token = create_access_token(user.id, role_name)
            return LoginUserResponseSchema(access_token=token, token_type="Bearer", role=role_name)

    async def refresh_google_token(self, refresh_token: str):
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

    @staticmethod
    async def register_with_otp(data, db: Session):
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Generate OTP
        email_service = EmailService()
        otp = email_service.generate_otp()
        otp_expiry = email_service.get_otp_expiry()
        
        # Create user with OTP
        password = hash_password(data.password)
        user = User(
            full_name=data.full_name, 
            email=data.email, 
            password=password, 
            gender=data.gender, 
            phone_number=data.phone_number,
            status=0,  # Not verified
            otp_code=otp,
            otp_expired_at=otp_expiry,
            otp_type=OTPType.REGISTER
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Send OTP email
        await email_service.send_otp_email(data.email, otp, "REGISTER")
        
        return user

    @staticmethod
    async def verify_otp(email: str, otp: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.otp_code != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        if user.otp_expired_at < datetime.now():
            raise HTTPException(status_code=400, detail="OTP expired")
        
        # Verify user
        user.status = 1
        user.otp_code = None
        user.otp_expired_at = None
        user.otp_type = None
        db.commit()
        
        return user
