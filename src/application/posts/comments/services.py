from typing import Optional

from sqlmodel import Session

from src.interface.posts.comments.schemas import CommentPost
from src.domain.posts.comments.services import CommentService
from src.domain.models import Comments
from src.application.posts.services import PostAppService


class CommentAppService:
    """comment application service for handling comments operation"""
    def __init__(self, session:Session):
        self.db_session = session
        self.comment_service = CommentService(session=self.db_session)

    def comment_post(self, comment:CommentPost) -> Optional[Comments]:
        """comment on post for post_id"""
        post_app_service = PostAppService(session=self.db_session)
        post = post_app_service.get_post_by_id(id=comment.post_id)
        if post:
            return self.comment_service.create_comment(comment=comment)
        return None