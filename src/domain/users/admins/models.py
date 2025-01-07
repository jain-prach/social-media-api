import uuid
from sqlmodel import Field, Relationship

from ..models import BaseUser
from lib.fastapi.custom_models import BaseModel


class Admin(BaseModel):
    """
    :model: for admin user management
    """

    user_id: uuid.UUID = Field(foreign_key="base_user.id", ondelete="CASCADE")
    user: BaseUser = Relationship()
