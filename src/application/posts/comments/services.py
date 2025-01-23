from typing import Optional
import uuid

from sqlmodel import Session

from src.interface.posts.comments.schemas import CommentPost
from src.domain.posts.comments.services import CommentService
from src.domain.models import Comments
from src.application.posts.services import PostAppService
from lib.fastapi.custom_exceptions import NotFoundException
from lib.fastapi.error_string import get_post_not_found


class CommentAppService:
    """comment application service for handling comments operation"""

    def __init__(self, session: Session):
        self.db_session = session
        self.comment_service = CommentService(session=self.db_session)

    def get_comment_by_comment_id(self, comment_id: uuid.UUID) -> Optional[Comments]:
        """get comment by comment id"""
        return self.comment_service.get_comment_by_id(id=comment_id)

    def comment_post(self, comment: CommentPost) -> Optional[Comments]:
        """comment on post for post_id"""
        post_app_service = PostAppService(session=self.db_session)
        post = post_app_service.get_post_by_id(id=comment.post_id)
        if not post:
            raise NotFoundException(get_post_not_found())
        return self.comment_service.create(comment=comment)

    def remove_comment(self, commented_by:uuid.UUID, comment_id: uuid.UUID) -> None:
        """remove comment from the post"""
        db_comment = self.get_comment_by_comment_id(comment_id=comment_id)
        if db_comment:
            if db_comment.commented_by == commented_by:
                self.comment_service.delete(db_comment=db_comment)
        return None