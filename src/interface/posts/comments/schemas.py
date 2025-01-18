import uuid
from pydantic import BaseModel

class CommentPostSchema(BaseModel):
    """schema to comment post"""
    comment: str
    post_id: str

class CommentPost(BaseModel):
    """schema to create comment in database"""
    commented_by: uuid.UUID
    comment: str
    post_id: uuid.UUID