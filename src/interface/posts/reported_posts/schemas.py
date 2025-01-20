import uuid
from typing import Optional

from pydantic import BaseModel

from lib.fastapi.custom_enums import ReportReason
from lib.fastapi.custom_schemas import BaseResponseNoDataSchema


class ReportPostSchema(BaseModel):
    """schema to report posts"""

    reason: ReportReason
    additional_text: Optional[str] = None


class ReportPostData(BaseModel):
    """schema to add report post in database"""

    reported_by: uuid.UUID
    post_id: uuid.UUID
    reason: ReportReason
    additional_text: Optional[str] = None


class ReportPostResponseData(BaseResponseNoDataSchema):
    """report post response data with message attribute set to static string value"""

    message: Optional[str] = "Post Reported!"
