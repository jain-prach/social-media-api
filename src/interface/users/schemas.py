import uuid
import re

from pydantic import BaseModel, EmailStr, field_validator

from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_schemas import BaseResponseSchema
from src.setup.config.settings import settings


class BaseUser(BaseModel):
    """base user schema without password"""

    email: EmailStr
    role: Role


class CreateBaseUser(BaseUser):
    """Create base user: includes password field for registration"""

    password: str

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(settings.STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Max length(8) and Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit and "
                "special symbol"
            )
        return password


class BaseUserResponse(BaseUser):
    """Base user response: includes ID field"""

    id: uuid.UUID


class BaseUserResponseData(BaseResponseSchema):
    data: BaseUserResponse
