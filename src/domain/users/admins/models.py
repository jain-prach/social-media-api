from typing import TYPE_CHECKING
import uuid
from sqlmodel import Field, Relationship

from lib.fastapi.custom_models import BaseModel

if TYPE_CHECKING:
    from src.domain.models import BaseUser


class Admin(BaseModel, table=True):
    """
    :model: for admin user management
    """

    base_user_id: uuid.UUID = Field(
        index=True, foreign_key="baseuser.id", ondelete="CASCADE"
    )
    base_user: "BaseUser" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="admin"
    )
