from typing import IO, Optional
import uuid

from sqlmodel import Session
from fastapi import UploadFile

from src.domain.models import User
from src.domain.users.users.services import UserService
from src.interface.users.users.schemas import UserWithProfile, UserWithBaseUserId
from src.infrastructure.file_upload.services import Boto3Service


class UserAppService:
    """services for user model"""

    def __init__(self, session: Session):
        self.db_session = session
        self.user_service = UserService(session=self.db_session)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """get user by username"""
        return self.user_service.get_user_by_username(username=username)

    def get_user_by_id(self, id: uuid.UUID) -> Optional[User]:
        """get user by id"""
        return self.user_service.get_user_by_id(id=id)

    def get_user_by_base_user_id(self, base_user_id: uuid.UUID) -> Optional[User]:
        """get user by base_user_id"""
        return self.user_service.get_user_by_base_user_id(base_user_id=base_user_id)

    def create_user(self, user: UserWithBaseUserId | UserWithProfile) -> User:
        """create user"""
        return self.user_service.create_user(user=user)
    
    def update_user(self, user: UserWithBaseUserId | UserWithProfile, db_user=User) -> User:
        """update user"""
        return self.user_service.update_user(user=user, db_user=db_user)
    
    def delete_user(self, id:uuid.UUID) -> None:
        user = self.get_user_by_id(id=id)
        if not user:
            return None
            # raise NotFoundException(get_user_not_found())
        self.user_service.delete_user(user=user)
        return None

    def upload_file_using_boto3(
        self, object_key: str, file: IO, file_type: str
    ) -> None:
        """upload file to minio from file stream"""
        Boto3Service().upload_file_from_memory(
            object_key=object_key, file_content=file, file_type=file_type
        )

    def handle_profile_upload(
        self, profile: UploadFile, user: UserWithBaseUserId
    ) -> str:
        """create object key and handle file upload"""
        get_file_extension = str(profile.filename).split(".")[-1]
        object_key = (
            f"profiles/{user.base_user_id}/{user.base_user_id}.{get_file_extension}"
        )
        self.upload_file_using_boto3(
            object_key=object_key, file=profile.file, file_type=profile.content_type
        )
        return object_key