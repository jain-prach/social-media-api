import uuid
from typing import Optional
from datetime import datetime, timedelta

from passlib.context import CryptContext

from sqlmodel import Session, select


from src.domain.models import BaseUser, Otp
from src.interface.users.schemas import CreateBaseUser, Login
from src.infrastructure.email_service.services import SendgridService
from src.infrastructure.auth_service.services import JWTService
from lib.fastapi.custom_exceptions import UnauthorizedException, NotFoundException
from lib.fastapi.error_string import get_user_not_found, get_incorrect_password, get_invalid_otp, get_expired_otp
from lib.fastapi.custom_enums import Role
from src.setup.config.settings import settings
from .tasks import delete_otp
from lib.fastapi.utils import get_default_timezone


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


class UserService:
    """services for base user model"""

    def __init__(self, session: Session):
        self.db_session = session

    def get_user_by_email(self, email: str) -> BaseUser:
        """get user from database using email value"""
        return self.db_session.scalars(
            select(BaseUser).where(BaseUser.email == email)
        ).first()
    
    def get_user_by_id(self, id:uuid.UUID) -> BaseUser:
        """get user by id"""
        return self.db_session.get(BaseUser, id)

    def create_user(self, user: CreateBaseUser) -> BaseUser:
        """create user in the database"""
        user.password = PasswordService().get_hashed_password(user.password)
        # print(user)
        db_user = BaseUser.model_validate(user)
        self.db_session.add(db_user)
        self.db_session.commit()
        self.db_session.refresh(db_user)
        return db_user

    def authenticate_user(self, user: Login) -> Optional[BaseUser]:
        """authenticate user for email and password"""
        db_user = self.get_user_by_email(user.email)
        if not db_user:
            raise NotFoundException(get_user_not_found())
        verify = PasswordService().verify_password(
            password=user.password, hashed_password=db_user.password
        )
        if not verify:
            raise UnauthorizedException(get_incorrect_password())
        return db_user

    def create_jwt_token_for_user(self, id: str, role: Role) -> str:
        """create jwt token with id in payload"""
        return JWTService().create_access_token(data={"id": id, "role": str(role)})

    def create_otp(self, user_id: uuid.UUID):
        """create otp for user"""
        db_otp = Otp.model_validate({"user_id": user_id})
        self.db_session.add(db_otp)
        self.db_session.commit()
        self.db_session.refresh(db_otp)
        return db_otp
    
    def get_otp_by_user_id(self, user_id: uuid.UUID):
        """get otp by user id"""
        otp = self.db_session.scalars(
            select(Otp).where(Otp.user_id == user_id)
        ).first()
        return otp
    
    def get_otp_by_otp_token(self, otp_token:str):
        """get otp by otp_token"""
        otp = self.db_session.scalars(
            select(Otp).where(Otp.otp_token == otp_token)
        ).first()
        return otp

    def forgot_password(self, email: str):
        """send email with otp for password forget"""
        user = self.get_user_by_email(email=email)

        #delete otp if already exists and create new
        otp_obj = self.get_otp_by_user_id(user.id)
        if otp_obj:
            # print("***", otp_obj)
            self.db_session.delete(otp_obj)

        otp = self.create_otp(user_id=user.id)
        # create celery task to delete otp from database after OTP_EXPIRE_TIME
        delete_otp.apply_async(
            kwargs={"user_id": user.id},
            eta=datetime.now(tz=get_default_timezone())
            + timedelta(**settings.OTP_EXPIRE_TIME),
        )
        ForgotPasswordService().send_otp_email(otp=otp.otp, user=user)
        return True
    
    def verify_otp(self, otp:int, user_id: uuid.UUID) -> str:
        """verify otp sent by the user to allow for password update"""
        otp_obj = self.get_otp_by_user_id(user_id=user_id)
        if otp_obj:
            if otp_obj.otp == otp:
                return otp_obj.otp_token
            raise UnauthorizedException(get_invalid_otp())
        else:
            raise NotFoundException(get_expired_otp())
    
    def set_new_password(self, user_id:uuid.UUID, new_password:str):
        """set new password for the given user"""
        user = self.get_user_by_id(id=user_id)
        user.password = PasswordService().get_hashed_password(new_password)
        self.db_session.add(user)
        self.db_session.commit()
        self.db_session.refresh(user)
        return user
    
    def reset_password(self, otp_token:str, new_password:str):
        """reset password using otp_token"""
        otp_obj = self.get_otp_by_otp_token(otp_token=otp_token)
        if otp_obj:
            return self.set_new_password(user_id=otp_obj.user_id, new_password=new_password)
        raise NotFoundException(get_expired_otp())