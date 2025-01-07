import uuid
from sqlmodel import Field, Relationship, Column, Enum

from ..models import BaseUser
from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import ProfileType


class User(BaseModel):
    """
    :model: for regular user management (app users without admin rights)
    """

    user_id: uuid.UUID = Field(foreign_key="base_user.id", ondelete="CASCADE")
    user: BaseUser = Relationship()
    username: str = Field(unique=True, nullable=False)
    bio: str = Field(default=None, nullable=True)
    profile: str = Field(default=None, nullable=True)
    is_verified: bool = Field(default=False, nullable=False)
    profile_type: ProfileType = Field(
        default=ProfileType.PUBLIC, nullable=False, sa_column=Column(Enum(ProfileType))
    )