import uuid
from typing import List

from sqlmodel import Session

from src.domain.posts.services import PostService
from src.interface.posts.schemas import PostSchema
from src.domain.models import Post
from lib.fastapi.custom_exceptions import NotFoundException
from lib.fastapi.error_string import get_post_not_found

class PostAppService:
    """handle post application services"""
    def __init__(self, session:Session):
        self.db_session = session
        self.post_service = PostService(session=self.db_session)

    def get_post_by_id(self, id:uuid.UUID) -> Post:
        """get post using post id"""
        post = self.post_service.get_post_by_id(id=id)
        if not post:
            raise NotFoundException(get_post_not_found())
        return post
    
    def get_all_posts_by_user(self, user_id:uuid.UUID) -> List[Post]:
        """get all posts posted by the user"""
        return self.post_service.get_all_posts_by_user(user_id=user_id)
    
    def get_post_by_post_id_for_user(self, post_id:uuid.UUID, user_id:uuid.UUID) -> Post:
        """get post by post_id from user's post"""
        post = self.get_post_by_id(id=post_id)
        if not post or post.posted_by != user_id:
            raise NotFoundException(get_post_not_found())
        return post

    def create_post(self, post:PostSchema) -> Post:
        """create new post"""
        db_post = self.post_service.create_post(post=post)
        return db_post

    def update_post(self, post_id:uuid.UUID, post:PostSchema) -> Post:
        """update post"""
        db_post = self.get_post_by_post_id_for_user(post_id=post_id, user_id=post.posted_by)
        return self.post_service.update_post(post=post, db_post=db_post)
    
    def delete_post(self, post_id:uuid.UUID, user_id:uuid.UUID) -> None:
        """delete post"""
        db_post = self.get_post_by_post_id_for_user(post_id=post_id, user_id=user_id)
        #delete from minio
        
        self.post_service.delete_post(db_post=db_post)