import uuid
from typing import Optional, TYPE_CHECKING, List

from sqlmodel import Field, Relationship

from lib.fastapi.custom_models import BaseModel

if TYPE_CHECKING:
    from .likes.models import Likes
    from .comments.models import Comments
    from .media.models import Media
    from .reported_posts.models import ReportPost

class Post(BaseModel, table=True):
    """:model: for user's post management"""

    posted_by:uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    caption:Optional[str] = Field(default=None)

    media: List['Media'] = Relationship(back_populates="post", sa_relationship_kwargs={"cascade": "delete"})
    likes: List['Likes'] = Relationship(back_populates="post", sa_relationship_kwargs={"cascade": "delete"})
    comments: List['Comments'] = Relationship(back_populates="post", sa_relationship_kwargs={"cascade": "delete"})
    report: List['ReportPost'] = Relationship(back_populates="post", sa_relationship_kwargs={"cascade": "delete"})