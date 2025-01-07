import uuid
import re

from pydantic import BaseModel, EmailStr, field_validator

from lib.fastapi.custom_enums import Role
from src.setup.config.settings import settings


class BaseUser(BaseModel):
    """base user schema for validating input fields"""

    email: EmailStr
    password: str
    role: Role

    @field_validator("password", mode="after")
    @classmethod
    def valid_password(cls, password: str) -> str:
        if not re.match(settings.STRONG_PASSWORD_PATTERN, password):
            raise ValueError(
                "Max length(8) and Password must contain at least "
                "one lower character,"
                "one upper character,"
                "digit and"
                "special symbol"
            )
        return password


class BaseUserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: Role
