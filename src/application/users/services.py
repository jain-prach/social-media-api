import uuid
from typing import Optional, List
from datetime import datetime, timedelta

from passlib.context import CryptContext

from sqlmodel import Session


from src.domain.models import BaseUser, Otp
from src.domain.users.services import BaseUserService, OtpService
from src.interface.auth.schemas import Login
from src.interface.users.schemas import CreateBaseUser, UpdateBaseUser
from src.infrastructure.email_service.services import SendgridService
from src.infrastructure.auth_service.services import JWTService
from src.infrastructure.oauth_service.services import GithubOauthService
from lib.fastapi.custom_exceptions import UnauthorizedException, NotFoundException
from lib.fastapi.error_string import get_user_not_found, get_incorrect_password, get_invalid_otp, get_expired_otp, get_git_email_not_found
from lib.fastapi.custom_enums import Role
from src.setup.config.settings import settings
from .tasks import delete_otp
from lib.fastapi.utils import get_default_timezone, db_session_value_create


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
            sender="prachi1.citrusbug@gmail.com",
            receivers=[
                {
                    "email": user.email,
                    "name": user.user.username if user.user else "User",
                }
            ],
            template_id=settings.FORGOT_PASSWORD_TEMPLATE,
            template_dict={
                "otp": str(otp),
                "user_id": f"{user.id}",
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
    
    def get_base_user_by_id(self, id:uuid.UUID) -> Optional[BaseUser]:
        """get base user by id"""
        return self.base_user_service.get_base_user_by_id(id=id)
    
    def get_all_base_users(self) -> List[BaseUser]:
        """returns list of all base users"""
        return self.base_user_service.get_all_base_users()

    def create_base_user(self, user: CreateBaseUser) -> BaseUser:
        """create base user after hashing base user's password"""
        user.password = PasswordService().get_hashed_password(user.password)
        return self.base_user_service.create_base_user(user)
    
    def create_base_user_without_password(self, email:str) -> BaseUser:
        """create base user without admin rights with only email - use for oauth"""
        return self.base_user_service.create_base_user(user={"email": email, "role": Role.USER})
    
    def update_base_user(self, user: UpdateBaseUser) -> BaseUser:
        """update base user email and role"""
        db_user = self.get_base_user_by_id(user.id)
        if not db_user:
            raise NotFoundException(detail=get_user_not_found())
        return self.base_user_service.update_base_user(user=user, db_user=db_user)

    def authenticate_user(self, user: Login) -> Optional[BaseUser]:
        """authenticate user for email and password"""
        db_user = self.get_base_user_by_email(user.email)
        if not db_user:
            raise UnauthorizedException(get_incorrect_password())
            # raise NotFoundException(get_user_not_found())
        verify = PasswordService().verify_password(
            password=user.password, hashed_password=db_user.password
        )
        if not verify:
            raise UnauthorizedException(get_incorrect_password())
        return db_user

    def create_jwt_token_for_user(self, id: str, role: Role) -> str:
        """create jwt token with id in payload"""
        return JWTService().create_access_token(data={"id": id, "role": role.value})
    
    def delete_base_user(self, id:uuid.UUID) -> None:
        user = self.get_base_user_by_id(id=id)
        if not user:
            return None
            # raise NotFoundException(get_user_not_found())
        self.base_user_service.delete_base_user(user=user)
        return None

    def create_otp(self, user_id: uuid.UUID) -> Otp:
        """create otp for user"""
        return OtpService(session=self.db_session).create_otp(user_id=user_id)
    
    def get_otp_by_base_user_id(self, user_id: uuid.UUID) -> Optional[Otp]:
        """get otp by user id"""
        return OtpService(session=self.db_session).get_otp_by_base_user_id(user_id=user_id)
    
    def get_otp_by_otp_token(self, otp_token:str) -> Optional[Otp]:
        """get otp by otp_token"""
        return OtpService(session=self.db_session).get_otp_by_otp_token(otp_token=otp_token)

    def forgot_password(self, email: str) -> None:
        """send email with otp for password forget"""
        user = self.get_base_user_by_email(email=email)
        if not user:
            return None
    
        #delete otp if already exists and create new
        otp_obj = self.get_otp_by_base_user_id(user.id)
        if otp_obj:
            OtpService(session=self.db_session).delete_otp()

        otp = self.create_otp(user_id=user.id)

        # create celery task to delete otp from database after OTP_EXPIRE_TIME
        delete_otp.apply_async(
            kwargs={"user_id": user.id},
            eta=datetime.now(tz=get_default_timezone())
            + timedelta(**settings.OTP_EXPIRE_TIME),
        )

        #send otp email using sendgrid
        ForgotPasswordService().send_otp_email(otp=otp.otp, user=user)

        return None

    
    def verify_otp(self, otp:int, user_id: uuid.UUID) -> str:
        """verify otp sent by the user to allow for password update"""
        otp_obj = self.get_otp_by_base_user_id(user_id=user_id)
        if otp_obj:
            if otp_obj.otp == otp:
                return otp_obj.otp_token
            raise UnauthorizedException(get_invalid_otp())
        else:
            raise NotFoundException(get_expired_otp())
    
    def set_new_password(self, user_id:uuid.UUID, new_password:str) -> BaseUser:
        """set new password for the given user"""
        user = self.get_base_user_by_id(id=user_id)
        user.password = PasswordService().get_hashed_password(new_password)
        # db_user = BaseUser.sqlmodel_update(user)
        ###CHECK
        return db_session_value_create(session=self.db_session, value=user)
        
    
    def reset_password(self, otp_token:str, new_password:str) -> BaseUser:
        """reset password using otp_token"""
        otp_obj = self.get_otp_by_otp_token(otp_token=otp_token)
        if otp_obj:
            return self.set_new_password(user_id=otp_obj.user_id, new_password=new_password)
        raise NotFoundException(get_expired_otp())
    
    @staticmethod
    def get_git_auth_url() -> str:
        """return git authentication url"""
        return GithubOauthService().get_auth_url()
    
    @staticmethod
    def get_git_user_email(code:str) -> Optional[str]:
        """return user email as available in user's git account"""
        access_token = GithubOauthService().get_access_token(code=code)
        email = GithubOauthService().get_user_email(access_token)
        if email:
            return email
        raise NotFoundException(get_git_email_not_found())