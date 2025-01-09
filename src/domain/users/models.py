from typing import Optional, TYPE_CHECKING
import uuid
import binascii
import os

from sqlmodel import Field, Column, Enum, Relationship

# from src.domain.models import Admin, User
from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import Role
from lib.fastapi.utils import generate_otp

if TYPE_CHECKING:
    from src.domain.models import Admin, User
class BaseUser(BaseModel, table=True):
    """
    :model: base user model for login and role management
    """
    email: str = Field(unique=True, nullable=False)
    password: Optional[str] = Field()
    role: Role = Field(default=Role.USER, sa_column=Column(Enum(Role)))
    is_active: Optional[bool] = Field(default=True, nullable=False)
    admin: Optional["Admin"] = Relationship(back_populates="base_user")
    user: Optional["User"] = Relationship(back_populates="base_user")

class Otp(BaseModel, table=True):
    """
    :model: otp model for otp management
    """
    otp:int = Field(default=generate_otp())
    user_id: uuid.UUID = Field(foreign_key="baseuser.id", ondelete="CASCADE", unique=True)
    otp_token:str = Field(default=binascii.hexlify(os.urandom(20)).decode(), nullable=False)