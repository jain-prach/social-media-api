import uuid
from sqlmodel import Field, Relationship

from ..models import BaseUser
from lib.fastapi.custom_models import BaseModel


class Admin(BaseModel, table=True):
    """
    :model: for admin user management
    """

    user_id: uuid.UUID = Field(foreign_key="baseuser.id", ondelete="CASCADE")
    user: BaseUser = Relationship()
