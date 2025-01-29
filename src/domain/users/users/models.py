from typing import TYPE_CHECKING, Optional, List
import uuid
from sqlmodel import Field, Relationship, Column, Enum

from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import ProfileType

if TYPE_CHECKING:
    from src.domain.models import BaseUser, FollowersModel, Subscription, Transaction


class User(BaseModel, table=True):
    """
    :model: for regular user management (app users without admin rights)
    """

    base_user_id: uuid.UUID = Field(
        index=True, foreign_key="baseuser.id", ondelete="CASCADE", unique=True
    )
    username: str = Field(index=True, unique=True, nullable=False)
    bio: str = Field(default=None, nullable=True)
    profile: Optional[str] = Field(default=None, nullable=True)
    is_verified: bool = Field(default=False, nullable=False)
    profile_type: ProfileType = Field(
        default=ProfileType.PUBLIC, sa_column=Column(Enum(ProfileType))
    )

    base_user: "BaseUser" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="user"
    )
    followers: List["FollowersModel"] = Relationship(
        back_populates="following",
        cascade_delete=True,
        sa_relationship_kwargs={
            "primaryjoin": "User.id == FollowersModel.following_id"
        },
    )
    following: List["FollowersModel"] = Relationship(
        back_populates="follower",
        cascade_delete=True,
        sa_relationship_kwargs={"primaryjoin": "User.id == FollowersModel.follower_id"},
    )
    subscription: Optional["Subscription"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    transaction: Optional["Transaction"] = Relationship(
        back_populates="user", cascade_delete=True
    )
