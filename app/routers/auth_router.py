from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.security import require_role
from app.db.base import get_db
from app.schemas.user_schemas import RegisterUserSchema, UserSchema, LoginUserSchema, LoginUserResponseSchema, VerifyOtpSchema
from app.services.auth_service import AuthService
from app.schemas.base_schema import DataResponse
from fastapi.responses import RedirectResponse
from app.core.config import settings
from urllib.parse import urlencode
from app.schemas.password_schema import ForgotPasswordOtpSchema, ResetPasswordOtpSchema, ResetPasswordSchema
from app.services.password_service import PasswordService
from app.services.user_service import UserService

router = APIRouter()

@router.post("/register", tags=["auth"], description="Register a new user with OTP", response_model=DataResponse[UserSchema])
async def register_user(data: RegisterUserSchema, db: Session = Depends(get_db)):
    try:
        user = await UserService.register_with_otp(data, db)
        return DataResponse.custom_response(code="201", message="OTP sent to email. Please verify to complete registration.", data=user)
    except HTTPException as e:
        return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)
    except Exception as e:
        # return DataResponse.custom_response(code="500", message="Register user failed", data=None)
        return DataResponse.custom_response(code="500", message=str(e), data=None)

@router.post("/verify-otp", tags=["auth"], description="Verify OTP for registration", response_model=DataResponse[UserSchema])
async def verify_otp(data: VerifyOtpSchema, db: Session = Depends(get_db)):
    try:
        user = await UserService.verify_otp(data.email, data.otp, db)
        return DataResponse.custom_response(code="200", message="Email verified successfully", data=user)
    except HTTPException as e:
        return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)

@router.post("/login", tags=["auth"], description="Login a user", response_model=DataResponse[LoginUserResponseSchema])
async def login_user(data: LoginUserSchema, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        response_data = auth_service.login_user(data)
        return DataResponse.custom_response(code="200", message="Login user success", data=response_data)
    except HTTPException as e:
        return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)
    except Exception as e:
         return DataResponse.custom_response(code="500", message="Login failed", data=None)

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

@router.get("/login/oauth2/code/google", tags=["auth"], description="Google Auth Callback", response_model=DataResponse[LoginUserResponseSchema])
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")
    
    auth_service = AuthService(db)
    try:
        data = await auth_service.google_login(code)
        return DataResponse.custom_response(
            code="200", 
            message="Login google success", 
            data=data
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return DataResponse.custom_response(code="500", message=str(e), data=None)

@router.post("/refresh-token", tags=["auth"], description="Refresh Google Token")
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        token_data = await auth_service.refresh_google_token(refresh_token)
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


@router.post("/reset-password-otp", tags=["auth"])
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

@router.post("/change-password", tags=["auth"])
async def change_password(
    data: ResetPasswordSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["user", "admin"]))
):
    PasswordService.change_password(
        current_user["user_id"],
        data.new_password,
        db
    )

    return DataResponse.custom_response(
        code="200",
        message="Password changed successfully",
        data=None
    )
