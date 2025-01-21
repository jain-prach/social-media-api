import uuid
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Column, Enum, Relationship

from lib.fastapi.custom_enums import ServiceModel, TransactionStatus


if TYPE_CHECKING:
    from src.domain.models import Subscription

class Transaction(SQLModel, table=True):
    """Transaction model for tracking payments"""

    payment_id: str = Field(index=True)
    base_user_id: uuid.UUID = Field(index=True)
    amount: float = Field(default=5)
    service_type: str = Field(
        default=ServiceModel.SUBSCRIPTION, sa_column=Column(Enum(ServiceModel))
    )
    status: str = Field(
        default=TransactionStatus.PROCESSING, sa_column=Column(Enum(TransactionStatus))
    )

    subscription: Optional["Subscription"] = Relationship(back_populates="transaction")