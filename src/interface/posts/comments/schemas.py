import uuid
from typing import Optional, Annotated

from pydantic import BaseModel, StringConstraints

from lib.fastapi.custom_schemas import BaseResponseNoDataSchema, BaseResponseSchema


class CommentPostSchema(BaseModel):
    """schema to comment post"""

    comment: Annotated[str, StringConstraints(strip_whitespace=True, max_length=300)]


class CommentPost(CommentPostSchema):
    """schema to create comment in database"""

    commented_by: uuid.UUID
    post_id: uuid.UUID


class CommentPostResponse(CommentPost):
    """comment post response for comment response with comment id"""

    id: uuid.UUID


class CommentPostResponseData(BaseResponseSchema):
    """comment post response data with message attribute set to static string value"""

    data: CommentPostResponse


class CommentDeleteResponseData(BaseResponseNoDataSchema):
    """comment delete response data with message attribute set to static string value"""

    message: Optional[str] = "Comment Deleted!"
