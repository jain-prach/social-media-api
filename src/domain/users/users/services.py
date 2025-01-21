from typing import Optional, List
import uuid

from sqlmodel import Session, select

from src.interface.users.users.schemas import UserWithProfile, UserWithBaseUserId
from .models import User
from lib.fastapi.utils import db_session_value_create


class UserService:
    """user service for managing database operations for User Model"""

    def __init__(self, session: Session):
        self.db_session = session

    def get_user_by_username(self, username: str) -> Optional[User]:
        """get user by username from the database"""
        return self.db_session.scalars(
            select(User).where(User.username == username)
        ).first()

    def get_user_by_id(self, id: uuid.UUID) -> Optional[User]:
        """get user by id from the database"""
        return self.db_session.get(User, id)

    def get_user_by_base_user_id(self, base_user_id: uuid.UUID) -> Optional[User]:
        """get user by base_user_id from the database"""
        return self.db_session.scalars(
            select(User).where(User.base_user_id == base_user_id)
        ).first()

    def get_all_users(self) -> List[User]:
        """get all users from the database"""
        return self.db_session.exec(select(User)).all()

    def create(self, user: UserWithBaseUserId | UserWithProfile) -> User:
        """create user in the database"""
        db_user = User.model_validate(user)
        db_session_value_create(session=self.db_session, value=db_user)
        return db_user

    def update(
        self, user: UserWithBaseUserId | UserWithProfile, db_user: User
    ) -> User:
        """update user in the database"""
        db_user.sqlmodel_update(user)
        db_session_value_create(session=self.db_session, value=db_user)
        return db_user

    def delete(self, user: User) -> None:
        """delete user in the database"""
        self.db_session.delete(user)
        self.db_session.commit()
