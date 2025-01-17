import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from lib.fastapi.custom_models import BaseModel

if TYPE_CHECKING:
    from ..models import Post

class Likes(BaseModel, table=True):
    """:model: for post's like management"""

    liked_by: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    post_id: uuid.UUID = Field(foreign_key="post.id", ondelete="CASCADE")
    
    post: 'Post' = Relationship(back_populates="likes")