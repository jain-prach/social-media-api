import uuid
from typing import List, Optional

from sqlmodel import Session, select

from .models import Post
from src.interface.posts.schemas import PostSchema
from lib.fastapi.utils import db_session_value_create

class PostService:
    """post service for handling post database operations"""
    def __init__(self, session:Session):
        self.db_session = session

    def get_post_by_id(self, id:uuid.UUID) -> Optional[Post]:
        """get post by post id"""
        return self.db_session.get(Post, id)
    
    def get_all_posts_by_user_id(self, user_id:uuid.UUID) -> List[Post]:
        """get all posts posted by the user using user id from database"""
        posts = self.db_session.scalars(select(Post).where(Post.posted_by == user_id))
        return posts
    
    # def get_post_by_post_id_for_user(self, post_id:uuid.UUID, user_id:uuid.UUID) -> Optional[Post]:
    #     """get post by post id that is posted by the user from the database"""
    #     return self.db_session.scalars(select(Post).where(Post.posted_by == user_id).where(Post.id == post_id))

    def create_post(self, post:PostSchema) -> Post:
        """create post in the database"""
        db_post = Post.model_validate(post)
        db_session_value_create(session=self.db_session, value=db_post)
        return db_post
    
    def update_post(self, post:PostSchema, db_post:Post) -> Post:
        """update post in the database"""
        db_post.sqlmodel_update(post)
        db_session_value_create(session=self.db_session, value=db_post)
        return db_post
    
    def delete_post(self, db_post:Post) -> None:
        """delete post from the database"""
        self.db_session.delete(db_post)
        self.db_session.commit()