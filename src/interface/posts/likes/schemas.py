import uuid
from pydantic import BaseModel

class LikePostSchema(BaseModel):
    """schema to like post"""

    post_id: str

class LikePost(BaseModel):
    """schema to create like in database"""
    liked_by: uuid.UUID
    post_id: uuid.UUID