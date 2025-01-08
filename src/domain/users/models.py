from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, Column, Enum, Relationship

# from src.domain.models import Admin, User
from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import Role

if TYPE_CHECKING:
    from src.domain.models import Admin, User
class BaseUser(BaseModel, table=True):
    """
    :model: base user model for login and role management
    """
    email: str = Field(unique=True, nullable=False)
    password: str = Field()
    role: Role = Field(default=Role.USER, sa_column=Column(Enum(Role)))
    is_active: Optional[bool] = Field(default=True, nullable=False)
    admin: Optional["Admin"] = Relationship(back_populates="base_user")
    user: Optional["User"] = Relationship(back_populates="base_user")