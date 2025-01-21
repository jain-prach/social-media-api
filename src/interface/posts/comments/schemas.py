import uuid
from typing import Optional

from pydantic import BaseModel

from lib.fastapi.custom_schemas import BaseResponseNoDataSchema


class CommentPostSchema(BaseModel):
    """schema to comment post"""
    comment: str

class CommentPost(BaseModel):
    """schema to create comment in database"""
    commented_by: uuid.UUID
    comment: str
    post_id: uuid.UUID

class CommentPostResponseData(BaseResponseNoDataSchema):
    """comment post response data with message attribute set to static string value"""

    message: Optional[str] = "Commented on post!"

class CommentDeleteResponseData(BaseResponseNoDataSchema):
    """comment delete response data with message attribute set to static string value"""

    message: Optional[str] = "Comment Deleted!"