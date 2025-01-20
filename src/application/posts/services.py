import uuid
from typing import List, Optional

from sqlmodel import Session

from src.domain.posts.services import PostService
from src.interface.posts.schemas import PostSchema
from src.application.users.users.services import UserAppService
from src.domain.models import Post
from lib.fastapi.custom_exceptions import NotFoundException
from lib.fastapi.error_string import get_post_not_found, get_user_not_found
from lib.fastapi.custom_enums import FilterDates
from src.infrastructure.file_upload.services import Boto3Service


class PostAppService:
    """handle post application services"""

    def __init__(self, session: Session):
        self.db_session = session
        self.post_service = PostService(session=self.db_session)

    def get_post_by_id(self, id: uuid.UUID) -> Optional[Post]:
        """get post using post id"""
        post = self.post_service.get_post_by_id(id=id)
        if not post:
            # raise NotFoundException(get_post_not_found())
            return None
        return post

    def get_all_posts_by_user_id(self, user_id: uuid.UUID) -> List[Post]:
        """get all posts posted by the user"""
        return self.post_service.get_all_posts_by_user_id(user_id=user_id)
    
    def get_all_posts_by_username(self, current_user_id:uuid.UUID, username:str, search: Optional[str], filter_by: Optional[FilterDates]) -> List[Post]:
        """get all posts by username"""
        user_app_service = UserAppService(session=self.db_session)
        user = user_app_service.get_user_by_username(username=username)
        if not user:
            raise NotFoundException(get_user_not_found())
        user_app_service.check_private_user(current_user_id=current_user_id, user=user)
        return self.post_service.get_all_posts_by_user_id(user_id=user.id, search=search, filter_by=filter_by)

    def get_post_by_post_id_for_user(
        self, post_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Post]:
        """get post by post_id from user's post"""
        post = self.get_post_by_id(id=post_id)
        if not post or post.posted_by != user_id:
            # raise NotFoundException(get_post_not_found())
            return None
        return post

    def create_post(self, post: PostSchema) -> Post:
        """create new post"""
        db_post = self.post_service.create(post=post)
        return db_post

    def update_post(self, post_id: uuid.UUID, post: PostSchema) -> Post:
        """update post"""
        db_post = self.get_post_by_post_id_for_user(
            post_id=post_id, user_id=post.posted_by
        )
        if not db_post:
            raise NotFoundException(get_post_not_found())
        return self.post_service.update(post=post, db_post=db_post)

    def delete_post(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """delete post"""
        db_post = self.get_post_by_post_id_for_user(post_id=post_id, user_id=user_id)
        if not db_post:
            return None
        # delete from minio
        for file in db_post.media:
            Boto3Service().delete_file(object_key=file.media_url)
        self.post_service.delete(db_post=db_post)