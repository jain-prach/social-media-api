import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field

from .utils import get_default_timezone

class BaseModel(SQLModel, table=False):
    """
    :model: custom base model to inherit to create new models in this codebase

    `field`
        :id: primary key with default value uuid.uuid4
        :created_at: contains default value as current time
        :modified_at: null at the time of model field creation
    """

    id: uuid.UUID = Field(default=uuid.uuid4(), primary_key=True)
    created_at: datetime = Field(
        default=datetime.now(tz=get_default_timezone()), nullable=False
    )
    modified_at: datetime = Field(nullable=True)
