import uuid
import re
from typing import Optional, List, Annotated

from pydantic import BaseModel, field_validator, field_serializer, StringConstraints

from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema
from lib.fastapi.custom_enums import ProfileType
from lib.fastapi.error_string import get_username_value_error
from src.setup.config.settings import settings
from src.infrastructure.file_upload.services import Boto3Service


class UsernameSchema(BaseModel):
    """username schema with validation"""

    username: str

    @field_validator("username", mode="after")
    @classmethod
    def valid_username(cls, username: str) -> str:
        if not re.match(settings.VALID_USERNAME_PATTERN, username):
            raise ValueError(get_username_value_error())
        return username


class UserSchema(UsernameSchema):
    """user schema"""

    # bio: constr(strip_whitespace=True, max_length=80)
    bio: Annotated[str, StringConstraints(strip_whitespace=True, max_length=80)]
    profile_type: ProfileType


class UserWithBaseUserId(UserSchema):
    """user schema with base user id to create relation to base user"""

    base_user_id: Optional[str] | Optional[uuid.UUID]


class UserWithProfile(UserWithBaseUserId):
    """user profile schema"""

    profile: str


class UserResponse(UserSchema):
    """user response valid fields"""

    profile: Optional[str]

    @field_serializer("profile")
    def serialize_profile(self, profile: str):
        if profile:
            boto3_service = Boto3Service()
            presigned_url = boto3_service.get_presigned_url(object_key=profile)
            return presigned_url
        return None


class UserResponseData(BaseResponseSchema):
    """user response data with data attribute to include UserResponse"""

    data: UserResponse


class UserListResponseData(BaseResponseSchema):
    """user list response data with data attribute to include UserResponse List"""

    data: List[UserResponse]


class GetUser(UsernameSchema):
    """information required to get user"""

    pass


class DeleteUserResponseData(BaseResponseNoDataSchema):
    """delete user response with message attribute set to constant string value"""

    message: Optional[str] = "User Deleted!"
