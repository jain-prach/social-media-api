from typing import Optional
import uuid

from pydantic import BaseModel

from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema
from lib.fastapi.custom_enums import SubscriptionInterval


class PaymentSuccessResponseData(BaseResponseNoDataSchema):
    """payment success response with message attribute set to static string"""

    message: Optional[str] = "Successful payment!"


class PaymentCancelResponseData(BaseResponseNoDataSchema):
    """payment cancel response with message attribute set to static string"""

    message: Optional[str] = "Payment Cancelled!"


class SubscriptionSchema(BaseModel):
    """subscription for database"""

    transaction_id: Optional[uuid.UUID]
    user_id: uuid.UUID
    interval: SubscriptionInterval
    is_cancelled: Optional[bool] = False

class SubscriptionResponseData(BaseResponseSchema):
    """subscription response data with data attribute set to subscription schema"""

    data: SubscriptionSchema
