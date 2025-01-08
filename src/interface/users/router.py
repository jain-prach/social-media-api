from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from .schemas import CreateBaseUser, BaseUserResponseData, Login, LoginResponseData, ForgotPassword, ForgotPasswordResponseData, VerifyOtp, VerifyOtpResponseData, ResetPassword, ResetPasswordResponseData
from src.setup.config.database import SessionDep
from src.application.users.services import UserService
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from .dependencies import AuthDep

router = APIRouter(tags=["auth"], route_class=UniqueConstraintErrorRoute)


@router.post(
    "/register/", status_code=HTTP_201_CREATED, response_model=BaseUserResponseData
)
def register(user: CreateBaseUser, session: SessionDep):
    """create base user for site access"""
    db_user = UserService(session).create_user(user)
    return {
        "message": "New user created",
        "success": True,
        "data": dict(**db_user.model_dump()),
    }


@router.post("/login/", status_code=HTTP_200_OK, response_model=LoginResponseData)
def login(user: Login, session: SessionDep):
    """login using base user credentials, use response access_token to login from HTTPBearer"""
    user_service = UserService(session)
    db_user = user_service.authenticate_user(user)
    access_token = user_service.create_jwt_token_for_user(id=str(db_user.id), role=db_user.role)
    return {
        "data": dict(
            id=db_user.id,
            email=db_user.email,
            access_token=access_token,
            token_type="bearer",
        )
    }

@router.post("/forgot-password", status_code=HTTP_200_OK, response_model=ForgotPasswordResponseData)
def forgot_password(user_email: ForgotPassword, session:SessionDep):
    """forgot password for existing base user email"""
    user_service = UserService(session)
    user_service.forgot_password(email=user_email.email)
    return ForgotPasswordResponseData()

@router.post("/verify-otp", status_code=HTTP_200_OK, response_model=VerifyOtpResponseData)
def verify_otp(data: VerifyOtp, session:SessionDep):
    """verify otp and return otp token if verified"""
    user_service = UserService(session)
    otp_token = user_service.verify_otp(otp=data.otp, user_id=data.user_id)
    return {"data": dict(otp_token=otp_token)}

@router.post("/reset-password", status_code=HTTP_200_OK, response_model=ResetPasswordResponseData)
def reset_password(data: ResetPassword, session:SessionDep):
    """reset password for user"""
    user_service = UserService(session)
    user = user_service.reset_password(otp_token=data.otp_token, new_password=data.new_password)
    return ResetPasswordResponseData()


# @router.get("/")
# def test_login_access(user:AuthDep):
#     return f"Hello {user}!"