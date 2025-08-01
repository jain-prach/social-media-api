from fastapi import APIRouter, Request
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from src.setup.config.database import SessionDep
from src.application.users.services import BaseUserAppService
from .schemas import (
    Login,
    LoginResponseData,
    ForgotPassword,
    ForgotPasswordResponseData,
    VerifyOtp,
    VerifyOtpResponseData,
    ResetPassword,
    ResetPasswordResponseData,
    GitAuthenticateResponseData,
    AccessTokenResponseData,
)
from ..users.schemas import CreateBaseUser, BaseUserResponseData
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from src.setup.config.limiter import limiter

router = APIRouter(tags=["auth"], route_class=UniqueConstraintErrorRoute)


@router.post(
    "/register/",
    status_code=HTTP_201_CREATED,
    response_model=BaseUserResponseData,
)
@limiter.limit("10/minute", override_defaults=True)
def register(request: Request, user: CreateBaseUser, session: SessionDep):
    """create base user for site access"""
    db_user = BaseUserAppService(session).create_base_user(user)
    return {
        "message": "New user created successfully",
        "success": True,
        "data": db_user,
    }


@router.post("/login/", status_code=HTTP_200_OK, response_model=LoginResponseData)
def login(user: Login, session: SessionDep):
    """login using base user credentials, use response access_token to login from HTTPBearer"""
    base_user_app_service = BaseUserAppService(session)
    response = base_user_app_service.authenticate_user(user)
    return {"data": response}


@router.post("/refresh/", status_code=HTTP_200_OK, response_model=AccessTokenResponseData)
def get_access_token_from_refresh_token(refresh_token: str, session: SessionDep):
    """get access token from refresh token"""
    base_user_app_service = BaseUserAppService(session)
    access_token = base_user_app_service.get_access_token_from_refresh(
        token=refresh_token
    )
    return {"data": {"access_token": access_token, "token_type": "bearer"}}


@router.post(
    "/forgot-password/",
    status_code=HTTP_200_OK,
    response_model=ForgotPasswordResponseData,
)
def forgot_password(user: ForgotPassword, session: SessionDep):
    """forgot password for existing base user email"""
    base_user_app_service = BaseUserAppService(session)
    base_user_app_service.forgot_password(email=user.email)
    return {}


@router.post(
    "/verify-otp/", status_code=HTTP_200_OK, response_model=VerifyOtpResponseData
)
def verify_otp(data: VerifyOtp, session: SessionDep):
    """verify otp and return otp token if verified"""
    base_user_app_service = BaseUserAppService(session)
    otp_token = base_user_app_service.verify_otp(otp=data.otp, email=data.email)
    return {"data": dict(otp_token=otp_token)}


@router.post(
    "/reset-password/",
    status_code=HTTP_200_OK,
    response_model=ResetPasswordResponseData,
)
def reset_password(data: ResetPassword, session: SessionDep):
    """reset password for user"""
    base_user_app_service = BaseUserAppService(session)
    base_user_app_service.reset_password(
        otp_token=data.otp_token, new_password=data.new_password
    )
    return {}


@router.get(
    "/git-authenticate/",
    status_code=HTTP_200_OK,
    response_model=GitAuthenticateResponseData,
)
def git_authenticate():
    """get github authentication url"""
    auth_url = BaseUserAppService.get_git_auth_url()
    return {"data": dict(url=auth_url)}


@router.get("/git-callback/", status_code=HTTP_200_OK, response_model=LoginResponseData)
def git_callback(code: str, session: SessionDep):
    """git callback to handle github login for the user"""
    base_user_app_service = BaseUserAppService(session)
    email = base_user_app_service.get_git_user_email(code=code)

    # create user if doesn't exist
    user = base_user_app_service.get_base_user_by_email(email=email)
    if not user:
        user = base_user_app_service.create_base_user_without_password(email=email)
    # get access_token
    access_token = base_user_app_service.create_jwt_token_for_user(
        id=str(user.id), role=user.role
    )

    # provide user with access_token
    return {
        "data": dict(
            id=user.id,
            email=user.email,
            access_token=access_token,
            token_type="bearer",
        )
    }
