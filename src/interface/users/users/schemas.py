import uuid
import re
from typing import Optional, List

from pydantic import BaseModel, field_validator

from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema
from lib.fastapi.custom_enums import ProfileType
from lib.fastapi.error_string import get_username_value_error
from src.setup.config.settings import settings


class UserSchema(BaseModel):
    """user schema"""

    username: str
    bio: str
    profile_type: ProfileType

    @field_validator("username", mode="after")
    @classmethod
    def valid_username(cls, username: str) -> str:
        if not re.match(settings.VALID_USERNAME_PATTERN, username):
            raise ValueError(get_username_value_error())
        return username

class UserWithBaseUserId(UserSchema):
    """user schema with base user id to create relation to base user"""

    base_user_id: Optional[str] | Optional[uuid.UUID]


class UserWithProfile(UserWithBaseUserId):
    """user profile schema"""

    profile: str


class UserResponse(UserSchema):
    """user response valid fields"""

    profile: Optional[str]


class UserResponseData(BaseResponseSchema):
    """user response data with data attribute to include UserResponse"""

    data: UserResponse


class UserListResponseData(BaseResponseSchema):
    """user list response data with data attribute to include UserResponse List"""

    data: List[UserResponse]


class GetUser(BaseModel):
    """information required to get user"""

    username: str


class DeleteUserResponseData(BaseResponseNoDataSchema):
    """delete user response with message attribute set to constant string value"""

    message: Optional[str] = "User Deleted!"
