import uuid
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

    base_user_id: uuid.UUID

class UserWithProfile(UserWithBaseUserId):
    """user profile schema"""

    profile: str

class UserResponse(UserWithBaseUserId):
    """user response valid fields"""
    id: uuid.UUID
    
class UserResponseData(BaseResponseSchema):
    data: UserResponse