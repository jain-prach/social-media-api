import uuid
import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, HttpUrl

from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema

from src.setup.config.settings import settings


class Login(BaseModel):
    """login schema for base user login"""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """login response schema with id and access_token"""

    id: uuid.UUID
    email: EmailStr
    access_token: str
    token_type: str


class LoginResponseData(BaseResponseSchema):
    """login response data with data attribute to include LoginResponse"""

    data: LoginResponse


class ForgotPassword(BaseModel):
    """Forgot Password update fields required"""

    email: EmailStr


class ForgotPasswordResponseData(BaseResponseNoDataSchema):
    """password response data with message attribute set to constant string value"""

    message: Optional[str] = "Otp will be sent if the user exists!"


class VerifyOtp(BaseModel):
    """verify otp schema, also verifies whether otp is of 4 digits"""

    otp: int
    email: EmailStr

    @field_validator("otp", mode="after")
    @classmethod
    def valid_otp(cls, otp: int) -> int:
        if not otp > 100000 and not otp < 999999:
            raise ValueError("Otp must be of 6 digit!")
        return otp


class VerifyOtpResponse(BaseModel):
    """send otp_token to user"""

    otp_token: str


class VerifyOtpResponseData(BaseResponseSchema):
    """verify otp data with data attribute to include VerifyOtpResponse"""

    data: VerifyOtpResponse


class ResetPassword(BaseModel):
    """reset password schema"""

    otp_token: str
    new_password: str

    @field_validator("new_password", mode="after")
    @classmethod
    def valid_password(cls, new_password: str) -> str:
        if not re.match(settings.STRONG_PASSWORD_PATTERN, new_password):
            raise ValueError(
                "Max length(8) and Password must contain at least "
                "one lower character, "
                "one upper character, "
                "digit and "
                "special symbol"
            )
        return new_password


class ResetPasswordResponseData(BaseResponseNoDataSchema):
    """reset password response data with message attribute set to constant string value"""

    message: Optional[str] = "New password set!"


class GitAuthenticateResponse(BaseModel):
    """git authentication url response schema"""

    url: HttpUrl

class GitAuthenticateResponseData(BaseResponseSchema):
    """git authentication response data with data attribute to include GitAuthenticateResponse"""

    data: GitAuthenticateResponse