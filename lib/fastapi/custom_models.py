import uuid
from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field

from .utils import get_default_timezone


class BaseModel(SQLModel, table=False):
    """:model: custom base model to inherit to create new models in this codebase"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=get_default_timezone()), nullable=False
    )
    modified_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(tz=get_default_timezone()),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(tz=get_default_timezone()),
        },
    )
