from typing import Optional

from sqlmodel import Session

from src.interface.posts.likes.schemas import LikePost
from src.domain.posts.likes.services import LikeService
from src.domain.models import Likes
from src.application.posts.services import PostAppService
from src.application.users.users.services import UserAppService


class LikeAppService:
    """like application service for handling likes operation"""

    def __init__(self, session: Session):
        self.db_session = session
        self.like_service = LikeService(session=self.db_session)

    def get_like_by_post_id_and_user_id(
        self, like:LikePost
    ) -> Optional[Likes]:
        """get like instance by post id and user id"""
        return self.like_service.get_like_by_post_id_and_user_id(
            post_id=like.post_id, liked_by=like.liked_by
        )

    def like_post(self, like: LikePost) -> Optional[Likes]:
        """like post for post_id"""
        post_app_service = PostAppService(session=self.db_session)
        post = post_app_service.get_post_by_id(id=like.post_id)
        # liked_by_list = [like.liked_by for like in post.likes] # and like.liked_by not in liked_by_list
        if not post:
            return None
        user_app_service = UserAppService(session=self.db_session)
        liked_by = user_app_service.get_user_by_id(id=like.liked_by)
        posted_by = user_app_service.get_user_by_id(id=post.posted_by)
        user_app_service.check_private_user(
            current_user={
                "id": str(liked_by.base_user_id),
                "role": liked_by.base_user.role,
            },
            user=posted_by,
        )
        return self.like_service.create(like=like)

    def remove_like(self, like:LikePost) -> None:
        """remove like from the post"""
        db_like = self.get_like_by_post_id_and_user_id(like=like)
        if db_like:
            self.like_service.delete(db_like=db_like)
        return None