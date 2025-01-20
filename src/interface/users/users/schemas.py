import uuid
from typing import Optional, List
from pydantic import BaseModel

from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema
from lib.fastapi.custom_enums import ProfileType


class UserSchema(BaseModel):
    """user schema"""

    username: str
    bio: str
    profile_type: ProfileType


class UserWithBaseUserId(UserSchema):
    """user schema with base user id to create relation to base user"""

    base_user_id: str | uuid.UUID


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
