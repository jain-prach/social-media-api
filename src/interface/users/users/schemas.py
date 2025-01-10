import uuid
from typing import Optional
from pydantic import BaseModel

from lib.fastapi.custom_schemas import BaseResponseSchema
from lib.fastapi.custom_enums import ProfileType

class UserSchema(BaseModel):
    """user schema"""

    username:str
    bio:str
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


class GetUser(BaseModel):
    """information required to get user"""

    username: str

class DeleteUserResponseData(BaseResponseSchema):
    """delete user response with data attribute set to constant string value"""

    data: Optional[str] = "User Deleted!"