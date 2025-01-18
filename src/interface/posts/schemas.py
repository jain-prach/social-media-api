import uuid
from typing import List, Optional

from pydantic import BaseModel

from src.interface.posts.media.schemas import MediaSchema
from lib.fastapi.custom_schemas import BaseResponseSchema


class CreatePostSchema(BaseModel):
    """create post schema for validating create post fields"""

    caption: str


class PostSchema(CreatePostSchema):
    """post schema with user.id that created post"""

    posted_by: uuid.UUID


class UpdatePostSchema(CreatePostSchema):
    """update post schema for validating update post fields"""

    id: str


class PostResponse(PostSchema):
    """post response"""

    id: uuid.UUID
    media: List[MediaSchema]


class PostResponseData(BaseResponseSchema):
    """post response data with data attribute to include PostResponse"""

    data: PostResponse

class PostDeleteResponseData(BaseResponseSchema):
    """post delete response data with data attribute set to optional static string"""

    data: Optional[str] = "Post Deleted!"

class PostListResponseData(BaseResponseSchema):
    """post list response data with data attribute to include List of PostResponse"""

    data: List[PostResponse]