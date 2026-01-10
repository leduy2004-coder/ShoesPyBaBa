
from fastapi import APIRouter
from app.schemas.user_schemas import RegisterUserSchema, UserSchema, LoginUserSchema, LoginUserResponseSchema, UserProfileUpdate, UserProfileResponse
from app.schemas.common_schema import ResponseSchema
from app.middleware.authenticate import authenticate 
from app.models.user_model import User
from fastapi import APIRouter, HTTPException
from app.schemas.user_schemas import UserSchema
from app.db.base import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app.schemas.base_schema import DataResponse
from app.core.security import security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.services.user_service import UserService
from app.middleware.authenticate import authenticate
from app.schemas.password_schema import (
    ChangePasswordSchema,
    ForgotPasswordOtpSchema,
    ResetPasswordOtpSchema
)
from app.services.password_service import PasswordService
from app.core.config import settings
from app.models.user_model import User

security = HTTPBearer()

def current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    return authenticate(credentials, db)

router = APIRouter()

@router.get("/profile", tags=["users"], description="Get current user", response_model=DataResponse[UserSchema])
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user_service = UserService(db)
    current_user = user_service.get_profile(credentials.credentials)
    return DataResponse.custom_response(code="200", message="Get current user success", data=current_user)



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

@router.put("/update-profile", tags=["users"], description="Update user profile", response_model=DataResponse[UserProfileResponse])
def update_user_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(current_user_dependency)
):
    service = UserService(db)
    updated_profile = service.update_user_profile(current_user, data)
    return ResponseSchema.custom_response(
        code="200",
        message="Update user profile success",
        data=updated_profile
    )

# @router.post("/reset-password", tags=["auth"])
# async def reset_password(
#     data: ResetPasswordOtpSchema,
#     db: Session = Depends(get_db)
# ):
#     try:
#         result = await PasswordService.reset_password_with_otp(
#             data.email,
#             data.otp,
#             data.new_password,
#             db
#         )
#         return DataResponse.custom_response(
#             code="200",
#             message="Password reset successfully",
#             data=result
#         )
#     except HTTPException as e:
#         return DataResponse.custom_response(code=str(e.status_code), message=e.detail, data=None)

# @router.post("/change-password", tags=["users"], description="Đổi mật khẩu cho người dùng đang đăng nhập")
# async def change_password(
#     data: ChangePasswordSchema,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(authenticate) # Lấy thông tin user từ token
# ):
#     try:
#         await PasswordService.change_password(current_user, data, db)
#         return DataResponse.custom_response(
#             code="200",
#             message="Đổi mật khẩu thành công",
#             data=None
#         )
#     except HTTPException as e:
#         return DataResponse.custom_response(
#             code=str(e.status_code),
#             message=e.detail,
#             data=None
#         )
#     except Exception as e:
#         return DataResponse.custom_response(
#             code="500",
#             message=f"Đổi mật khẩu thất bại: {str(e)}",
#             data=None
#         )

