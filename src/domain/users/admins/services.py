import uuid

from sqlmodel import Session, select

from .models import Admin
from src.interface.users.admins.schemas import CreateAdmin
from lib.fastapi.utils import db_session_value_create


class AdminService:
    """admin service class for database operation"""

    def __init__(self, session: Session):
        self.db_session = session

    def get_admin_by_base_user_id(self, base_user_id: uuid.UUID) -> Admin:
        """get admin by base user id from the database"""
        return self.db_session.scalars(
            select(Admin).where(Admin.base_user_id == base_user_id)
        ).first()

    def create(self, admin: CreateAdmin) -> Admin:
        """create admin in the database"""
        return db_session_value_create(session=self.db_session, value=admin)

    def delete(self, admin: Admin) -> None:
        """delete admin from the database"""
        self.db_session.delete(admin)
        self.db_session.commit()
