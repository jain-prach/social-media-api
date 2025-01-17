import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from lib.fastapi.custom_models import BaseModel

if TYPE_CHECKING:
    from ..models import Post
    
class Comments(BaseModel, table=True):
    """:model: for post's comment management"""

    commented_by: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    post_id: uuid.UUID = Field(foreign_key="post.id", ondelete="CASCADE")
    comment:str = Field(min_length=10, max_length=300)
    
    post: 'Post' = Relationship(back_populates="comments")