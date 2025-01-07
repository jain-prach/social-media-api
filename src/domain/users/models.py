from sqlmodel import Field, Column, Enum

from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import Role


class BaseUser(BaseModel, table=True):
    """
    :model: base user model for login and role management
    """

    email: str = Field(unique=True, nullable=False)
    password: str = Field()
    role: Role = Field(default=Role.USER, sa_column=Column(Enum(Role)))
    is_active: bool = Field(default=True, nullable=False)
