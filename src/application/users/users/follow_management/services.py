import uuid
from typing import List, Optional

from sqlmodel import Session

from src.domain.models import FollowersModel, User
from src.domain.users.users.follow_management.services import FollowService
from src.application.users.users.services import UserAppService
from lib.fastapi.custom_exceptions import NotFoundException, CustomValidationError, BadRequestException
from lib.fastapi.error_string import (
    get_user_not_created,
    get_send_request_to_yourself,
    get_user_not_found,
    get_accept_request_for_no_follower,
    get_reject_request_for_no_follower
)
from lib.fastapi.custom_enums import StatusType, ProfileType
from src.interface.users.users.follow_management.schemas import FollowRequest


class FollowAppService:
    """services for follower model"""

    def __init__(self, session: Session):
        self.db_session = session
        self.follow_service = FollowService(session=self.db_session)

    def get_follow_by_follow_id(self, id: uuid.UUID) -> Optional[FollowersModel]:
        """get follow request using follow id"""
        return self.follow_service.get_follow_by_follow_id(id=id)

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
            raise NotFoundException(get_user_not_found())
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

    def get_followers(
        self, current_user: dict, username: str
    ) -> List[FollowersModel]:
        """get requests accepted by the user"""
        user = self.get_user_by_username(username=username)
        user_app_service = UserAppService(session=self.db_session)
        user_app_service.check_private_user(current_user=current_user, user=user)
        followers = self.get_all_followers(base_user_id=user.base_user_id)
        return [
            follower for follower in followers if follower.status == StatusType.APPROVED
        ]

    def get_following(
        self, current_user: dict, username: str
    ) -> List[FollowersModel]:
        """get sent requests accepted for the user"""
        user = self.get_user_by_username(username=username)
        user_app_service = UserAppService(session=self.db_session)
        user_app_service.check_private_user(current_user=current_user, user=user)
        following_list = self.get_all_following_list(base_user_id=user.base_user_id)
        return [
            following
            for following in following_list
            if following.status == StatusType.APPROVED
        ]

    def send_request(self, follower: User, user: User) -> FollowersModel:
        """send request to the user for private account"""
        follow = FollowRequest(
            follower_id=follower.id, following_id=user.id, status=StatusType.PENDING
        )
        return self.follow_service.create(follow=follow)

    def create_follower(self, follower: User, user: User) -> FollowersModel:
        """create follower of the user for public account"""
        follow = FollowRequest(
            follower_id=follower.id, following_id=user.id, status=StatusType.APPROVED
        )
        return self.follow_service.create(follow=follow)

    def create_follow_request(
        self, follower_base_user_id: uuid.UUID, username: str
    ) -> FollowersModel:
        """create follower request"""
        follower = self.get_user_by_base_user_id(base_user_id=follower_base_user_id)
        user = self.get_user_by_username(username=username)
        if user.username == follower.username:
            raise CustomValidationError(get_send_request_to_yourself())
        if user.profile_type == ProfileType.PRIVATE:
            return self.send_request(follower=follower, user=user)
        return self.create_follower(follower=follower, user=user)

    def accept_follow_request(
        self, base_user_id: uuid.UUID, accept_username: str
    ) -> Optional[FollowersModel]:
        """accept follow request"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        follower = self.get_user_by_username(username=accept_username)
        db_follow = self.follow_service.get_follow_for_follower_and_following(
            follower_id=follower.id, following_id=user.id
        )
        if not db_follow or (db_follow.status != StatusType.PENDING):
            raise BadRequestException(get_accept_request_for_no_follower())
        follow = FollowRequest(
            follower_id=follower.id, following_id=user.id, status=StatusType.APPROVED
        )
        return self.follow_service.update(follow=follow, db_follow=db_follow)

    def reject_follow_request(
        self, base_user_id: uuid.UUID, reject_username: str
    ) -> None:
        """reject follow request"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        rejected_user = self.get_user_by_username(username=reject_username)
        db_follow = self.follow_service.get_follow_for_follower_and_following(
            follower_id=rejected_user.id, following_id=user.id
        )
        if not db_follow or db_follow.status != StatusType.PENDING:
            raise BadRequestException(get_reject_request_for_no_follower())
        return self.follow_service.delete(db_follow=db_follow)

    def cancel_follow_request(
        self, base_user_id: uuid.UUID, cancel_username: str
    ) -> None:
        """cancel follow request"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        cancel_request_user = self.get_user_by_username(username=cancel_username)
        db_follow = self.follow_service.get_follow_for_follower_and_following(
            follower_id=user.id, following_id=cancel_request_user.id
        )
        if not db_follow or db_follow.status != StatusType.PENDING:
            return None
        return self.follow_service.delete(db_follow=db_follow)

    def unfollow(self, base_user_id: uuid.UUID, unfollow_username: str) -> None:
        """unfollow user"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        unfollow_user = self.get_user_by_username(username=unfollow_username)
        db_follow = self.follow_service.get_follow_for_follower_and_following(
            follower_id=user.id, following_id=unfollow_user.id
        )
        if not db_follow or db_follow.status != StatusType.APPROVED:
            return None
        return self.follow_service.delete(db_follow=db_follow)

    def remove_follower(self, base_user_id: uuid.UUID, remove_username: str) -> None:
        """remove follower"""
        user = self.get_user_by_base_user_id(base_user_id=base_user_id)
        remove_follower = self.get_user_by_username(username=remove_username)
        db_follow = self.follow_service.get_follow_for_follower_and_following(
            follower_id=remove_follower.id, following_id=user.id
        )
        if not db_follow or db_follow.status != StatusType.APPROVED:
            return None
        return self.follow_service.delete(db_follow=db_follow)
