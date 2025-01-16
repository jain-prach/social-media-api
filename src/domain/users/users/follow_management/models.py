import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Column, Enum, Relationship, UniqueConstraint

from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import StatusType

if TYPE_CHECKING:
    from src.domain.models import User


class FollowersModel(BaseModel, table=True):
    """
    :model: for follower and following list management
    """
    
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="RequestSent"),
    )
    
    follower_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    following_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    status: StatusType = Field(
        default=StatusType.PENDING, sa_column=Column(Enum(StatusType))
    )

    follower: "User" = Relationship(
        back_populates="following",
        sa_relationship_kwargs={
            "foreign_keys": "[FollowersModel.follower_id]",
        },
    )
    following: "User" = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={
            "foreign_keys": "[FollowersModel.following_id]",
        },
    )
