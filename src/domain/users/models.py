from typing import Optional, TYPE_CHECKING
import uuid

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
    email: str = Field(index=True, unique=True, nullable=False)
    password: Optional[str] = Field(default=None)
    role: Role = Field(default=Role.USER, sa_column=Column(Enum(Role)))
    is_active: Optional[bool] = Field(default=True, nullable=False)
    admin: Optional["Admin"] = Relationship(back_populates="base_user", cascade_delete=True)
    user: Optional["User"] = Relationship(back_populates="base_user", cascade_delete=True)
    otp: Optional["Otp"] = Relationship(back_populates="base_user", cascade_delete=True)

class Otp(BaseModel, table=True):
    """
    :model: otp model for otp management
    """
    otp:int = Field(default=generate_otp())
    base_user_id: uuid.UUID = Field(index=True, foreign_key="baseuser.id", ondelete="CASCADE", unique=True)

    base_user: "BaseUser" = Relationship(back_populates="otp")