from fastapi import APIRouter
from app.schemas.user_schemas import RegisterUserSchema, UserSchema, LoginUserSchema, LoginUserResponseSchema, UserProfileUpdate, UserProfileResponse
from app.schemas.common_schema import ResponseSchema
from app.middleware.authenticate import authenticate as get_current_user
from app.models.user_model import User
from app.db.base import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from app.schemas.base_schema import DataResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.middleware.authenticate import authenticate
from app.core.config import settings
import httpx
from urllib.parse import urlencode
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", tags=["users"], description="Register a new user", response_model=DataResponse[UserSchema])
async def register_user(data: RegisterUserSchema, db: Session = Depends(get_db)):
    password = hash_password(data.password)
    user = User(full_name=data.full_name, email=data.email, password=password, gender=data.gender, phone_number=data.phone_number)
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return DataResponse.custom_response(code="201", message="Register user success", data=user)
    except Exception as e:
        return DataResponse.custom_response(code="500", message="Register user failed", data=None)


@router.post("/login", tags=["users"], description="Login a user", response_model=DataResponse[LoginUserResponseSchema])
async def login_user(data: LoginUserSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return DataResponse.custom_response(code="401", message="Invalid email or password", data=None)
    if not verify_password(data.password, user.password):
        return DataResponse.custom_response(code="401", message="Invalid email or password", data=None)
    
    token = create_access_token(user.id)
    
    return DataResponse.custom_response(code="200", message="Login user success", data=LoginUserResponseSchema(access_token=token, token_type="Bearer"))

@router.get("/profile", tags=["users"], description="Get current user", response_model=DataResponse[UserSchema], dependencies=[Depends(authenticate)])
async def get_current_user(current_user: User = Depends(authenticate)):
    return DataResponse.custom_response(code="200", message="Get current user success", data=current_user)

@router.get("/login/google", tags=["auth"], description="Initiate Google Login")
def login_google():
    query_params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    url = f"{settings.GOOGLE_AUTH_ENDPOINT}?{urlencode(query_params)}"
    return RedirectResponse(url)

@router.get("/auth/callback", tags=["auth"], description="Google Auth Callback", response_model=DataResponse[LoginUserResponseSchema])
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")
    
    try:
        data = await UserService.google_login(code, db)
        return DataResponse.custom_response(
            code="200", 
            message="Login google success", 
            data=data
        )
    except Exception as e:
        # Re-raise HTTP exceptions or handle generic errors
        if isinstance(e, HTTPException):
            raise e
        return DataResponse.custom_response(code="500", message=str(e), data=None)

@router.post("/refresh-token", tags=["auth"], description="Refresh Google Token")
async def refresh_access_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    try:
        token_data = await UserService.refresh_google_token(refresh_token)
        return DataResponse.custom_response(
            code="200", 
            message="Refresh token success", 
            data=token_data
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return DataResponse.custom_response(code="500", message=str(e), data=None)

@router.put("/update-profile", tags=["users"], description="Update user profile", response_model=ResponseSchema[UserProfileResponse])
def update_user_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = UserService(db)
    updated_profile = service.update_user_profile(current_user, data)
    return ResponseSchema.custom_response(
        code="200",
        message="Update user profile success",
        data=updated_profile
    )