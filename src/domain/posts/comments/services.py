import uuid
from typing import Optional

from sqlmodel import Session

from .models import Comments
from src.interface.posts.comments.schemas import CommentPost
from lib.fastapi.utils import db_session_value_create

class CommentService:
    """handle comment database operations"""
    def __init__(self, session:Session):
        self.db_session = session

    def get_comment_by_id(self, id:uuid.UUID) -> Optional[Comments]:
        """get comment by comment id"""
        return self.db_session.get(Comments, id)
    
    def create(self, comment:CommentPost) -> Comments:
        """create comment on post"""
        db_comment = Comments.model_validate(comment)
        db_session_value_create(session=self.db_session, value=db_comment)
        return db_comment

    def delete(self, db_comment:Comments) -> None:
        """delete comment from the post"""
        self.db_session.delete(db_comment)
        self.db_session.commit()