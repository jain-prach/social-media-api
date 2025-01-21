import uuid
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from src.domain.models import Transaction

class Subscription(SQLModel, table=True):
    """Subscription model for handling subscribed users"""

    transaction_id:Optional[uuid.UUID] = Field(index=True, foreign_key="transaction.id", nullable=True)
    base_user_id: uuid.UUID = Field(index=True, unique=True)
    access_time: datetime = Field(nullable=False)

    transaction:Optional["Transaction"] = Relationship(back_populates="transaction")