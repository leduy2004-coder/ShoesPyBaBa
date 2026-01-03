from fastapi import APIRouter
from app.schemas.user_schemas import RegisterUserSchema, UserSchema, LoginUserSchema, LoginUserResponseSchema, VerifyOtpSchema
from app.models.user_model import User
from app.db.base import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.schemas.base_schema import DataResponse
from app.core.security import security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.user_service import UserService
from app.schemas.password_schema import (
    ForgotPasswordOtpSchema,
    ResetPasswordOtpSchema
)
from app.services.password_service import PasswordService
from app.core.config import settings


router = APIRouter()


@router.post("/register", tags=["users"], description="Register a new user with OTP", response_model=DataResponse[UserSchema])
async def register_user(data: RegisterUserSchema, db: Session = Depends(get_db)):
    try:
        user = await UserService.register_with_otp(data, db)
        return DataResponse.custom_response(code="201", message="OTP sent to email. Please verify to complete registration.", data=user)
    except HTTPException as e:
        return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)
    except Exception as e:
        # return DataResponse.custom_response(code="500", message="Register user failed", data=None)
        return DataResponse.custom_response(code="500", message=str(e), data=None)

@router.post("/verify-otp", tags=["users"], description="Verify OTP for registration", response_model=DataResponse[UserSchema])
async def verify_otp(data: VerifyOtpSchema, db: Session = Depends(get_db)):
    try:
        user = await UserService.verify_otp(data.email, data.otp, db)
        return DataResponse.custom_response(code="200", message="Email verified successfully", data=user)
    except HTTPException as e:
        return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)


@router.post("/login", tags=["users"], description="Login a user", response_model=DataResponse[LoginUserResponseSchema])
async def login_user(data: LoginUserSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return DataResponse.custom_response(code="401", message="Invalid email or password", data=None)
    if not verify_password(data.password, user.password):
        return DataResponse.custom_response(code="401", message="Invalid email or password", data=None)
    if user.status != 1:
        return DataResponse.custom_response(code="401", message="Please verify your email first", data=None)
    
    token = create_access_token(user.id)
    
    return DataResponse.custom_response(code="200", message="Login user success", data=LoginUserResponseSchema(access_token=token, token_type="Bearer"))

# @router.get("/profile", tags=["users"], description="Get current user", response_model=DataResponse[UserSchema], dependencies=[Depends(authenticate)])
# async def get_current_user(current_user: User = Depends(authenticate)):
#     return DataResponse.custom_response(code="200", message="Get current user success", data=current_user)

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
    
@router.post("/forgot-password", tags=["auth"])
async def forgot_password(
    data: ForgotPasswordOtpSchema,
    db: Session = Depends(get_db)
):
    try:
        result = await PasswordService.forgot_password_otp(data.email, db)
        return DataResponse.custom_response(
            code="200",
            message="OTP sent to email",
            data=result
        )
    except HTTPException as e:
        return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)


@router.post("/reset-password", tags=["auth"])
async def reset_password(
    data: ResetPasswordOtpSchema,
    db: Session = Depends(get_db)
):
    try:
        result = await PasswordService.reset_password_with_otp(
            data.email,
            data.otp,
            data.new_password,
            db
        )
        return DataResponse.custom_response(
            code="200",
            message="Password reset successfully",
            data=result
        )
    except HTTPException as e:
        return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)



@router.get("/profile", tags=["users"], description="Get current user", response_model=DataResponse[UserSchema])
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user_service = UserService(db)
    current_user = user_service.get_profile(credentials)
    return DataResponse.custom_response(code="200", message="Get current user success", data=current_user)



