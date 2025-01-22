import uuid
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Column, Enum, Relationship

from lib.fastapi.custom_enums import ServiceModel, TransactionStatus
from lib.fastapi.custom_models import BaseModel

if TYPE_CHECKING:
    from src.domain.models import Subscription, User


class Transaction(BaseModel, table=True):
    """Transaction model for tracking payments"""

    payment_id: str = Field(index=True)
    user_id: uuid.UUID = Field(index=True, foreign_key="user.id", ondelete="CASCADE")
    amount: int = Field(nullable=False)
    service_type: ServiceModel = Field(
        default=ServiceModel.SUBSCRIPTION, sa_column=Column(Enum(ServiceModel))
    )
    status: TransactionStatus = Field(
        default=TransactionStatus.PROCESSING, sa_column=Column(Enum(TransactionStatus))
    )

    subscription: Optional["Subscription"] = Relationship(back_populates="transaction")
    user: "User" = Relationship(back_populates="transaction")
