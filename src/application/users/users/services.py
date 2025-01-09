from typing import IO
from sqlmodel import Session

from src.domain.models import User
from lib.fastapi.utils import db_session_value_create
from src.infrastructure.file_upload.services import Boto3Service


class UserService:
    """services for user model"""

    def __init__(self, session: Session):
        self.db_session = session

    def create_user(self, user) -> User:
        """create user in the database"""
        # file
        db_user = User.model_validate(user)
        db_session_value_create(session=self.db_session, value=db_user)
        return db_user

    def upload_profile_using_boto3(
        self, object_key: str, file: IO, file_type: str
    ) -> None:
        Boto3Service().upload_file_from_memory(
            object_key=object_key, file_content=file, file_type=file_type
        )
