import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, UniqueConstraint, Column, Enum

from lib.fastapi.custom_models import BaseModel
from lib.fastapi.custom_enums import ReportReason

if TYPE_CHECKING:
    from ..models import Post
    
class ReportPost(BaseModel, table=True):
    """:model: for reported posts management"""
    __table_args__ = (
        UniqueConstraint("reported_by", "post_id", name="ReportedOnce"),
    )

    reported_by: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")
    post_id: uuid.UUID = Field(foreign_key="post.id", ondelete="CASCADE")
    reason:ReportReason = Field(sa_column=Column(Enum(ReportReason)))
    additional_text:str = Field(default=None)
    
    post: 'Post' = Relationship(back_populates="report")