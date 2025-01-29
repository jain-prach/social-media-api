import uuid
from typing import Optional, List
from datetime import datetime, timedelta

from passlib.context import CryptContext

from sqlmodel import Session


from src.domain.models import BaseUser, Otp
from src.domain.users.services import BaseUserService, OtpService
from src.interface.auth.schemas import Login
from src.interface.users.schemas import (
    CreateBaseUser,
    UpdateBaseUser
)
from src.infrastructure.email_service.services import SendgridService
from src.infrastructure.auth_service.services import JWTService
from src.infrastructure.oauth_service.services import GithubOauthService
from lib.fastapi.custom_exceptions import UnauthorizedException, NotFoundException, BadRequestException
from lib.fastapi.error_string import (
    get_user_not_found,
    get_incorrect_password,
    get_invalid_otp,
    get_expired_otp,
    get_git_email_not_found,
    get_otp_link_expired,
    get_invalid_otp_token
)
from lib.fastapi.custom_enums import Role, Environment
from src.setup.config.settings import settings
from .tasks import delete_otp
from lib.fastapi.utils import get_default_timezone
from src.application.users.users.services import UserAppService
from src.application.users.admins.services import AdminAppService


class PasswordService:
    """services for password handling"""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(PasswordService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_hashed_password(self, password: str) -> str:
        """create hashed password for the password string received by user"""
        return self.PASSWORD_CONTEXT.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """verify password string with the hashed_password"""
        return self.PASSWORD_CONTEXT.verify(password, hashed_password)


class ForgotPasswordService(SendgridService):
    """Email Service for Forgot Password to send otp"""

    def send_otp_email(self, otp: int, user: BaseUser):
        """sends otp to the user's email"""
        self._send_template_email(
            sender=settings.SENDGRID_SENDER,
            receivers=[
                {
                    "email": user.email,
                    "name": user.user.username if user.user else "User",
                }
            ],
            template_id=settings.FORGOT_PASSWORD_TEMPLATE,
            template_dict={
                "otp": str(otp),
            },
        )


class BaseUserAppService:
    """services for base user model"""

    def __init__(self, session: Session):
        self.db_session = session
        self.base_user_service = BaseUserService(session=self.db_session)

    def get_base_user_by_email(self, email: str) -> Optional[BaseUser]:
        """get base user by email value"""
        return self.base_user_service.get_base_user_by_email(email=email)

    def get_base_user_by_id(self, id: uuid.UUID) -> Optional[BaseUser]:
        """get base user by id"""
        return self.base_user_service.get_base_user_by_id(id=id)
    
    def get_base_user_by_user_id(self, user_id: uuid.UUID) -> Optional[BaseUser]:
        """get base user by user id"""
        return self.base_user_service.get_base_user_by_user_id(user_id=user_id)

    def get_all_base_users(self) -> List[BaseUser]:
        """returns list of all base users"""
        return self.base_user_service.get_all_base_users()

    def create_base_user(self, base_user: CreateBaseUser) -> BaseUser:
        """create base user after hashing base user's password"""
        base_user.password = PasswordService().get_hashed_password(base_user.password)
        db_base_user = self.base_user_service.create(base_user=base_user)
        if db_base_user.role == Role.ADMIN:
            admin_app_service = AdminAppService(session=self.db_session)
            db_base_user.admin = admin_app_service.create_admin_directly(base_user_id=db_base_user.id)
        else:
            user_app_service = UserAppService(session=self.db_session)
            db_base_user.user = user_app_service.create_dummy_user(base_user_id=db_base_user.id)
        return self.update_base_user(base_user=db_base_user)

    def create_base_user_without_password(self, email: str) -> BaseUser:
        """create base user without admin rights with only email - use for oauth"""
        return self.base_user_service.create(user={"email": email, "role": Role.USER})

    def update_base_user(self, base_user: BaseUser) -> BaseUser:
        """update base user"""
        db_base_user = self.get_base_user_by_id(base_user.id)
        if not db_base_user:
            raise NotFoundException(detail=get_user_not_found())
        return self.base_user_service.update(
            base_user=base_user, db_base_user=db_base_user
        )

    def authenticate_user(self, user: Login) -> Optional[BaseUser]:
        """authenticate user for email and password"""
        db_user = self.get_base_user_by_email(email=user.email)
        if not db_user:
            raise UnauthorizedException(get_incorrect_password())
        verify = PasswordService().verify_password(
            password=user.password, hashed_password=db_user.password
        )
        if not verify:
            raise UnauthorizedException(get_incorrect_password())
        return db_user

    def create_jwt_token_for_user(self, id: str, role: Role) -> str:
        """create jwt token with base user id and role in payload"""
        return JWTService().create_access_token(
            data={"id": id, "role": role.value},
            expire=datetime.now() + timedelta(**settings.ACCESS_TOKEN_LIFETIME),
        )

    def delete_base_user(self, id: uuid.UUID) -> None:
        db_base_user = self.get_base_user_by_id(id=id)
        if not db_base_user:
            return None
        self.base_user_service.delete(db_base_user=db_base_user)
        return None

    def create_otp(self, user_id: uuid.UUID) -> Otp:
        """create otp for user"""
        return OtpService(session=self.db_session).create(base_user_id=user_id)
    
    def delete_otp(self, user:BaseUser) -> None:
        """delete otp created for user"""
        otp_obj = user.otp
        if otp_obj:
            otp_service = OtpService(session=self.db_session)
            otp_service.delete(otp=otp_obj)
        return None

    def forgot_password(self, email: str) -> None:
        """send email with otp for password forget"""
        user = self.get_base_user_by_email(email=email)
        if not user:
            return None

        # delete otp if already exists and create new
        self.delete_otp(user=user)

        otp = self.create_otp(user_id=user.id)

        # create celery task to delete otp from database after OTP_EXPIRE_TIME
        delete_otp.apply_async(
            kwargs={"base_user_id": user.id},
            eta=datetime.now(tz=get_default_timezone())
            + timedelta(**settings.OTP_EXPIRE_TIME),
        )

        if settings.ENVIRONMENT != Environment.TESTING.value:
            # send otp email using sendgrid
            # print("sending email")
            ForgotPasswordService().send_otp_email(otp=otp.otp, user=user)

        return None

    def create_jwt_token_for_otp(self, otp: int, base_user_id: uuid.UUID) -> str:
        """create jwt token with otp and base_user_id in payload"""
        return JWTService().create_access_token(
            data={"id": base_user_id, "otp": otp},
            expire=datetime.now() + timedelta(**settings.OTP_EXPIRE_TIME),
        )

    def verify_otp(self, otp: int, email: str) -> str:
        """verify otp sent by the user to allow for password update"""
        base_user = self.get_base_user_by_email(email=email)
        otp_obj = base_user.otp
        if otp_obj:
            if otp_obj.otp == otp:
                return self.create_jwt_token_for_otp(
                    otp=otp_obj.otp, base_user_id=str(base_user.id)
                )
            raise UnauthorizedException(get_invalid_otp())
        else:
            raise NotFoundException(get_expired_otp())

    def set_new_password(self, user: BaseUser, new_password: str) -> BaseUser:
        """set new password for the given user"""
        db_user = user
        user.password = PasswordService().get_hashed_password(new_password)
        self.base_user_service.update(base_user=user, db_base_user=db_user)
        self.delete_otp(user=user)
        return user

    def reset_password(self, otp_token: str, new_password: str) -> BaseUser:
        """reset password using otp_token"""
        payload = JWTService().decode(token=otp_token)
        if not payload.get("id") or not payload.get("otp") or not payload.get("exp"):
            raise BadRequestException(get_invalid_otp_token())
        if datetime.fromtimestamp(payload.get("exp")) < datetime.now():
            raise NotFoundException(get_otp_link_expired())
        base_user_id = payload.get("id")
        user = self.get_base_user_by_id(id=base_user_id)
        if user.otp is None:
            raise NotFoundException(get_otp_link_expired())
        return self.set_new_password(user=user, new_password=new_password)

    @staticmethod
    def get_git_auth_url() -> str:
        """return git authentication url"""
        return GithubOauthService().get_auth_url()

    @staticmethod
    def get_git_user_email(code: str) -> Optional[str]:
        """return user email as available in user's git account"""
        access_token = GithubOauthService().get_access_token(code=code)
        email = GithubOauthService().get_user_email(access_token=access_token)
        if email:
            return email
        raise NotFoundException(get_git_email_not_found())
