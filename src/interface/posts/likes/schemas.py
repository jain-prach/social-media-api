from typing import Optional
import uuid
from pydantic import BaseModel

from lib.fastapi.custom_schemas import BaseResponseNoDataSchema

# class LikePostSchema(BaseModel):
#     """schema to like post"""

#     post_id: str

class LikePost(BaseModel):
    """schema to create like in database"""
    liked_by: uuid.UUID
    post_id: uuid.UUID

class LikePostResponseData(BaseResponseNoDataSchema):
    """like post response data with message attribute set to static string value"""

    message: Optional[str] = "Post Liked!"

class LikeDeleteResponseData(BaseResponseNoDataSchema):
    """like delete response data with message attribute set to static string value"""

    message: Optional[str] = "Post Unliked!"