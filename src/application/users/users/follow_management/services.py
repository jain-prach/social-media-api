import uuid
from typing import List, Optional

from sqlmodel import Session

from src.domain.models import FollowersModel, User
from src.domain.users.users.follow_management.services import FollowerService
from src.application.users.users.services import UserAppService
from lib.fastapi.custom_exceptions import NotFoundException, CustomValidationError
from lib.fastapi.error_string import get_user_not_created, get_send_request_to_yourself
from lib.fastapi.custom_enums import StatusType


class FollowerAppService:
    """services for follower model"""

    def __init__(self, session: Session):
        self.db_session = session
        self.follower_service = FollowerService(session=self.db_session)

    def get_follow_by_follow_id(self, id: uuid.UUID) -> Optional[FollowersModel]:
        return self.follower_service.get_follow_by_follow_id(id=id)

    def get_user_by_base_user_id(self, base_user_id: uuid.UUID) -> User:
        """get user by base user id, raise NotFoundException if user not created"""
        user = UserAppService(session=self.db_session).get_user_by_base_user_id(
            base_user_id=base_user_id
        )
        if not user:
            raise NotFoundException(get_user_not_created())
        return user

    def get_user_by_username(self, username: str) -> User:
        """get user by username, raise NotFoundException if user not created"""
        user = UserAppService(session=self.db_session).get_user_by_username(
            username=username
        )
        if not user:
            raise NotFoundException(get_user_not_created())
        return user

    def get_all_followers(self, base_user_id: uuid.UUID) -> List[FollowersModel]:
        """get all requests sent to user"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        return user.followers

    def get_all_following_list(self, base_user_id: uuid.UUID) -> List[FollowersModel]:
        """get all requests sent by user"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        return user.following

    def get_pending_requests_sent_to_user(
        self, base_user_id: uuid.UUID
    ) -> List[FollowersModel]:
        """get pending requests sent to user"""
        followers = self.get_all_followers(base_user_id=base_user_id)
        return [
            follower for follower in followers if follower.status == StatusType.PENDING
        ]

    def get_pending_requests_sent_by_user(
        self, base_user_id: uuid.UUID
    ) -> List[FollowersModel]:
        """get pending requests sent by user using"""
        following_list = self.get_all_following_list(base_user_id=base_user_id)
        return [
            following
            for following in following_list
            if following.status == StatusType.PENDING
        ]

    def get_followers(self, username: str) -> List[FollowersModel]:
        """get requests accepted by the user"""
        user = self.get_user_by_username(username=username)
        followers = self.get_all_followers(base_user_id=user.base_user_id)
        return [
            follower for follower in followers if follower.status == StatusType.APPROVED
        ]

    def get_following(self, username: str) -> List[FollowersModel]:
        """get sent requests accepted for the user"""
        user = self.get_user_by_username(username=username)
        following_list = self.get_all_following_list(base_user_id=user.base_user_id)
        return [
            following
            for following in following_list
            if following.status == StatusType.APPROVED
        ]

    def create_follow_request(
        self, follower_id: uuid.UUID, username: str
    ) -> FollowersModel:
        """create follower request"""
        follower = self.get_user_by_base_user_id(base_user_id=follower_id)
        user = self.get_user_by_username(username=username)
        if user.username == follower.username:
            raise CustomValidationError(get_send_request_to_yourself())
        return self.follower_service.create_follow_request(follower=follower, user=user)

    def accept_follow_request(
        self, base_user_id: uuid.UUID, accept_username: str
    ) -> Optional[FollowersModel]:
        """accept follow request"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        follower = self.get_user_by_username(username=accept_username)
        follow = self.follower_service.get_follow_for_follower_and_following(
            follower_id=follower.id, following_id=user.id
        )
        if not follow:
            return None
        self.follower_service.accept_follow_request(follow=follow)
        return follow