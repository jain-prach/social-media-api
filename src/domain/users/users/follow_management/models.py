import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Column, Enum, Relationship

from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import StatusType

if TYPE_CHECKING:
    from src.domain.models import User
class FollowersModel(BaseModel, table=True):
    """
    :model: for follower and following list management
    """

    follower_id:uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    follower:"User" = Relationship(back_populates="user.followers")
    following_id:uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    following:"User" = Relationship(back_populates="user.following")
    status: StatusType = Field(default=StatusType.PENDING, sa_column=Column(Enum(StatusType)))
