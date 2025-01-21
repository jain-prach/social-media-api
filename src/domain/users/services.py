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
    
    # def get_base_user_by_user_id(self, user_id:uuid.UUID) -> Optional[BaseUser]:
    #     """get base user from the database using user_id"""
    #     return self.db_session.scalars(select(BaseUser).join(User).filter(User.id == user_id).first())
    
    def get_all_base_users(self) -> List[BaseUser]:
        """returns list of all base users from the database"""
        users = self.db_session.exec(select(BaseUser)).all()
        return users
    
    def create(self, base_user: CreateBaseUser | BaseUserSchema) -> BaseUser:
        """create base user in the database"""
        db_base_user = BaseUser.model_validate(base_user)
        db_session_value_create(session=self.db_session, value=db_base_user)
        return db_base_user
    
    def update(self, base_user:UpdateBaseUser, db_base_user:BaseUser) -> BaseUser:
        """update base user in the database"""
        db_base_user.sqlmodel_update(base_user)
        db_session_value_create(session=self.db_session, value=db_base_user)
        return db_base_user
    
    def delete(self, db_base_user:BaseUser) -> None:
        self.db_session.delete(db_base_user)
        self.db_session.commit()
        # user.is_active = False
        # db_session_value_create(session=self.db_session, value=user)
    
class OtpService:
    """otp service class to handle Otp database operations"""
    def __init__(self, session:Session):
        self.db_session = session
    
    def create(self, base_user_id: uuid.UUID) -> Otp:
        """create otp for user"""
        db_otp = Otp.model_validate({"base_user_id": base_user_id})
        db_session_value_create(session=self.db_session, value=db_otp)
        return db_otp
    
    def delete(self, otp:Otp) -> None:
        self.db_session.delete(otp)
        self.db_session.commit()
    