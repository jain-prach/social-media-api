import uuid

from sqlmodel import Session, select

from .models import Likes
from src.interface.posts.likes.schemas import LikePost
from lib.fastapi.utils import db_session_value_create

class LikeService:
    """handle like database operations"""
    def __init__(self, session:Session):
        self.db_session = session

    def get_like_by_post_id_and_user_id(self, post_id:uuid.UUID, liked_by:uuid.UUID):
        """get like instance by post id and user id"""
        return self.db_session.scalars(
            select(Likes)
            .where(Likes.post_id == post_id)
            .where(Likes.liked_by == liked_by)
        ).first()
    
    def create(self, like:LikePost) -> Likes:
        """create like on post"""
        db_like = Likes.model_validate(like)
        db_session_value_create(session=self.db_session, value=db_like)
        return db_like

    def delete(self, db_like:Likes) -> None:
        """delete like from the post"""
        self.db_session.delete(db_like)
        self.db_session.commit()