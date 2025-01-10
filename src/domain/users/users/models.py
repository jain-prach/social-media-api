from typing import TYPE_CHECKING, Optional, List
import uuid
from sqlmodel import Field, Relationship, Column, Enum

from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import ProfileType

if TYPE_CHECKING:
    from src.domain.models import BaseUser
    from src.domain.models import FollowersModel


class User(BaseModel, table=True):
    """
    :model: for regular user management (app users without admin rights)
    """

    base_user_id: uuid.UUID = Field(foreign_key="baseuser.id", ondelete="CASCADE")
    base_user: "BaseUser" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="user"
    )
    username: str = Field(unique=True, nullable=False)
    bio: str = Field(default=None, nullable=True)
    profile: Optional[str] = Field(default=None, nullable=True)
    is_verified: bool = Field(default=False, nullable=False)
    profile_type: ProfileType = Field(
        default=ProfileType.PUBLIC, sa_column=Column(Enum(ProfileType))
    )
    followers: List["FollowersModel"] = Relationship(
        back_populates="followersmodel.followers",
        sa_relationship_kwargs={"primaryjoin": "user.id == following_id"},
    )
    following: List["FollowersModel"] = Relationship(
        back_populates="followersmodel.following",
        sa_relationship_kwargs={"primaryjoin": "user.id == follower_id"},
    )