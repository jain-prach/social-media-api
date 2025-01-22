import uuid

from pydantic import BaseModel

from lib.fastapi.custom_enums import ServiceModel, TransactionStatus

class TransactionSchema(BaseModel):
    """transaction schema for database"""

    payment_id: str
    user_id: uuid.UUID
    amount: int
    service_type: ServiceModel
    status: TransactionStatus