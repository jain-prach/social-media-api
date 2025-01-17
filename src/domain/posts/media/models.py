import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship
from lib.fastapi.custom_models import BaseModel

if TYPE_CHECKING:
    from ..models import Post
    
class Media(BaseModel, table=True):
    """:model: for post's media management"""

    post_id: uuid.UUID = Field(foreign_key="post.id", ondelete="CASCADE")
    media_url:str = Field()
    media_type:str = Field()

    post: 'Post' = Relationship(back_populates="media")
