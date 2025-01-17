from typing import Optional
import uuid

from sqlmodel import Session, select

from src.domain.models import FollowersModel, User
from lib.fastapi.custom_enums import StatusType
from lib.fastapi.utils import db_session_value_create


class FollowerService:
    """Follower Service class for managing database operations for follower Model"""

    def __init__(self, session: Session):
        self.db_session = session

    def get_follow_by_follow_id(self, id: uuid.UUID) -> Optional[FollowersModel]:
        """get follow request by FollowersModel id"""
        return self.db_session.get(FollowersModel, id)

    def get_follow_for_follower_and_following(
        self, follower_id: uuid.UUID, following_id: uuid.UUID
    ) -> Optional[FollowersModel]:
        """get follow request using follower_id and following_id"""
        return self.db_session.scalars(
            select(FollowersModel)
            .where(FollowersModel.follower_id == follower_id)
            .where(FollowersModel.following_id == following_id)
        ).first()

    def create_follow_request(self, follower: User, user: User, status:StatusType) -> FollowersModel:
        """create follow request with status pending"""
        follow = {
            "follower_id": follower.id,
            "following_id": user.id,
            "status": status,
        }
        db_follow = FollowersModel.model_validate(follow)
        db_session_value_create(session=self.db_session, value=db_follow)
        return db_follow

    def update_status(self, follow: FollowersModel, status:StatusType) -> FollowersModel:
        """updating follow request status"""
        db_follow = follow
        follow.status = status
        db_follow.sqlmodel_update(follow)
        db_session_value_create(session=self.db_session, value=db_follow)
        return db_follow
    
    def delete_follow_request(self, follow: FollowersModel) -> None:
        """deleting follow request for rejected status"""
        self.db_session.delete(follow)
        self.db_session.commit()