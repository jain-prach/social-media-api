from typing import Optional

from sqlmodel import Session

from src.interface.posts.likes.schemas import LikePost
from src.domain.posts.likes.services import LikeService
from src.domain.models import Likes
from src.application.posts.services import PostAppService


class LikeAppService:
    """like application service for handling likes operation"""
    def __init__(self, session:Session):
        self.db_session = session
        self.like_service = LikeService(session=self.db_session)

    def like_post(self, like:LikePost) -> Optional[Likes]:
        """like post for post_id"""
        post_app_service = PostAppService(session=self.db_session)
        post = post_app_service.get_post_by_id(id=like.post_id)
        liked_by_list = [like.liked_by for like in post.likes]
        if post and like.liked_by not in liked_by_list:
            return self.like_service.create_like(like=like)
        return None