from typing import Optional, List
import uuid

from sqlmodel import Session
from fastapi import UploadFile
from faker import Faker

from src.domain.models import User
from src.domain.users.users.services import UserService
from src.interface.users.users.schemas import UserWithProfile, UserWithBaseUserId
from src.infrastructure.file_upload.services import Boto3Service
from lib.fastapi.custom_enums import ProfileType, Role, StatusType
from lib.fastapi.custom_exceptions import ForbiddenException, CustomValidationError
from lib.fastapi.error_string import get_user_is_private, get_user_not_created
from lib.fastapi.utils import check_id


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

    def get_all_users(self) -> List[User]:
        """get all users list"""
        return self.user_service.get_all_users()

    def get_all_public_users(self) -> List[User]:
        """get all public users list"""
        return self.user_service.get_all_public_users()

    def create_user(self, user: UserWithBaseUserId | UserWithProfile) -> User:
        """create user"""
        return self.user_service.create(user=user)

    def update_user(self, user: UserWithBaseUserId | UserWithProfile) -> User:
        """update user"""
        db_user = self.get_user_by_base_user_id(base_user_id=user.base_user_id)
        if not db_user:
            raise CustomValidationError(get_user_not_created())
        if user.profile_type == ProfileType.PUBLIC:
            # get followers list with status type pending
            followers = [follower for follower in db_user.followers]
            # update all to status type approved
            for follower in followers:
                if follower.status == StatusType.PENDING:
                    follower.status = StatusType.APPROVED
        # if user.profile:
            #delete db_user profile (not needed because it will override)
        return self.user_service.update(user=user, db_user=db_user)

    def delete_user(self, base_user_id: uuid.UUID) -> None:
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        if not user:
            return None
        self.user_service.delete(user=user)
        return None

    def check_private_user(self, current_user: dict, user: User) -> None:
        """check if user is private and whether current user follows the user"""
        if current_user["role"] != Role.ADMIN.value:
            current_user_id = check_id(id=current_user.get("id"))
            db_user = self.get_user_by_base_user_id(base_user_id=current_user_id)
            if user.profile_type == ProfileType.PRIVATE:
                followers_user_id = [
                    follower.follower.id
                    for follower in user.followers
                    if follower.status == StatusType.APPROVED
                ]
                # print(user.followers)
                # print(followers_user_id)
                # print(db_user)
                if db_user.id == user.id:
                    return None
                if db_user.id not in followers_user_id:
                    raise ForbiddenException(get_user_is_private())

    def create_dummy_user(self, base_user_id: uuid.UUID) -> User:
        """create dummy user when base_user is created"""
        fake = Faker()
        user = UserWithBaseUserId(
            username=fake.user_name(),
            bio="update your bio",
            profile_type=ProfileType.PUBLIC,
            base_user_id=base_user_id,
        )
        db_user = self.create_user(user)
        return db_user

    @staticmethod
    def handle_profile_upload(profile: UploadFile, user: UserWithBaseUserId) -> str:
        """create object key and handle file upload"""
        get_file_extension = str(profile.filename).split(".")[-1]
        object_key = (
            f"profiles/{user.base_user_id}/{user.base_user_id}.{get_file_extension}"
        )
        boto3_service = Boto3Service()
        boto3_service.upload_file_from_memory(
            object_key=object_key,
            file_content=profile.file,
            file_type=profile.content_type,
        )
        return object_key
