from sqlmodel import Session

from .models import Likes
from src.interface.posts.likes.schemas import LikePost
from lib.fastapi.utils import db_session_value_create

class LikeService:
    """handle like database operations"""
    def __init__(self, session:Session):
        self.db_session = session
    
    def create_like(self, like:LikePost) -> Likes:
        """create like on post"""
        db_like = Likes.model_validate(like)
        db_session_value_create(session=self.db_session, value=db_like)
        return db_like

    def delete_like(self, db_like:Likes) -> None:
        """delete like from the post"""
        self.db_session.delete(db_like)
        self.db_session.commit()