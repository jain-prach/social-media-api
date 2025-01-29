import uuid
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, Column, Enum

from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import SubscriptionInterval


if TYPE_CHECKING:
    from src.domain.models import Transaction, User


class Subscription(BaseModel, table=True):
    """Subscription model for handling subscribed users"""

    transaction_id: Optional[uuid.UUID] = Field(
        index=True, foreign_key="transaction.id", nullable=True
    )
    user_id: uuid.UUID = Field(
        index=True, foreign_key="user.id", ondelete="CASCADE", unique=True
    )
    interval: SubscriptionInterval = Field(
        default=SubscriptionInterval.DAILY, sa_column=Column(Enum(SubscriptionInterval))
    )
    is_cancelled:bool = Field(default=False, nullable=False)
    transaction: Optional["Transaction"] = Relationship(back_populates="subscription")
    user: "User" = Relationship(back_populates="subscription")