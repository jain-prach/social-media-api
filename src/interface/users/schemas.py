import re
import uuid
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator

from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema
from lib.fastapi.error_string import get_password_value_error
from src.setup.config.settings import settings
from src.interface.users.users.schemas import UserResponse, UserWithBaseUserId
from src.interface.users.admins.schemas import AdminResponse, CreateAdmin


class BaseUserSchema(BaseModel):
    """base user schema without password"""

    email: EmailStr
    role: Role


class CreateBaseUser(BaseUserSchema):
    """Create base user: includes password field for registration"""

    password: str

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(settings.STRONG_PASSWORD_PATTERN, password):
            raise ValueError(get_password_value_error())
        return password


class BaseUserResponse(BaseUserSchema):
    """Base user response: includes ID field"""

    id: uuid.UUID
    user: Optional[UserResponse]
    admin: Optional[AdminResponse]


class BaseUserResponseData(BaseResponseSchema):
    """base user response data with data attribute to include BaseUserResponse"""

    data: BaseUserResponse


class BaseUserListResponseData(BaseResponseSchema):
    """response schema for base user list with data attribute to include List[BaseUserResponse]"""

    data: List[BaseUserResponse]


class GetBaseUser(BaseModel):
    """information required to get base user"""

    id: str | uuid.UUID


class UpdateBaseUser(BaseModel):
    """schema to upload base user"""

    id: str | uuid.UUID
    role: Role


class DeleteBaseUserResponseData(BaseResponseNoDataSchema):
    """delete base user response data with message attribute set to constant string value"""

    message: Optional[str] = "Base User Deleted!"
