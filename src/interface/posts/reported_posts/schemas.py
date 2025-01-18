import uuid
from typing import Optional

from pydantic import BaseModel

from lib.fastapi.custom_enums import ReportReason

class ReportPostSchema(BaseModel):
    """schema to report posts"""

    post_id:str
    reason: ReportReason
    additional_text:Optional[str] = None
    
class ReportPostData(BaseModel):
    """schema to add report post in database"""

    reported_by:uuid.UUID
    post_id:uuid.UUID
    reason: ReportReason
    additional_text:Optional[str] = None