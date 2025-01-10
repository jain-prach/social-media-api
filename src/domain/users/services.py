from typing import Optional, List
import uuid

from sqlmodel import Session, select

from src.interface.users.schemas import CreateBaseUser, BaseUserSchema, UpdateBaseUser
from lib.fastapi.utils import db_session_value_create
from .models import BaseUser, Otp


class BaseUserService:
    """base user service class to handle BaseUser database operations"""
    def __init__(self, session:Session):
        self.db_session = session

    def get_base_user_by_email(self, email: str) -> Optional[BaseUser]:
        """get base user from the database using email value returns None if value doesn't exist"""
        return self.db_session.scalars(
            select(BaseUser).where(BaseUser.email == email)
        ).first()
    
    def get_base_user_by_id(self, id:uuid.UUID) -> Optional[BaseUser]:
        """get base user from the database by id returns None if id doesn't exist"""
        return self.db_session.get(BaseUser, id)
    
    def get_all_base_users(self) -> List[BaseUser]:
        """returns list of all base users from the database"""
        users = self.db_session.exec(select(BaseUser)).all()
        return users
    
    def create_base_user(self, user: CreateBaseUser | BaseUserSchema) -> BaseUser:
        """create base user in the database"""
        db_user = BaseUser.model_validate(user)
        db_session_value_create(session=self.db_session, value=db_user)
        return db_user
    
    def update_base_user(self, user:UpdateBaseUser, db_user:BaseUser) -> BaseUser:
        """update base user (only role) in the database"""
        db_user.sqlmodel_update(user)
        db_session_value_create(session=self.db_session, value=db_user)
        return db_user
    
    def delete_base_user(self, user:BaseUser) -> None:
        self.db_session.delete(user)
        self.db_session.commit()
        # user.is_active = False
        # db_session_value_create(session=self.db_session, value=user)
    
class OtpService:
    """otp service class to handle Otp database operations"""
    def __init__(self, session:Session):
        self.db_session = session

    def get_otp_by_base_user_id(self, user_id: uuid.UUID) -> Optional[Otp]:
        return self.db_session.scalars(
            select(Otp).where(Otp.user_id == user_id)
        ).first()
    
    def get_otp_by_otp_token(self, otp_token:str) -> Optional[Otp]:
        return self.db_session.scalars(
            select(Otp).where(Otp.otp_token == otp_token)
        ).first()
    
    def create_otp(self, user_id: uuid.UUID) -> Otp:
        """create otp for user"""
        db_otp = Otp.model_validate({"user_id": user_id})
        db_session_value_create(session=self.db_session, value=db_otp)
        return db_otp
    
    def delete_otp(self, otp:Otp) -> None:
        self.db_session.delete(otp)
        self.db_session.commit()
    