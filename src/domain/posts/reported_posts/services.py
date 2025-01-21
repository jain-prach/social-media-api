import uuid
from typing import Optional, List

from sqlmodel import Session, select

from .models import ReportPost
from src.interface.posts.reported_posts.schemas import ReportPostData
from lib.fastapi.utils import db_session_value_create

class ReportPostService:
    """handle database operations for reporting a post"""
    def __init__(self, session:Session):
        self.db_session = session

    def get_reported_post_by_id(self, id:uuid.UUID) -> Optional[ReportPost]:
        """get reported post by id from the database"""
        return self.db_session.get(ReportPost, id)
    
    def get_all_reported_posts(self) -> List[ReportPost]:
        """get all reported posts from the database"""
        return self.db_session.exec(select(ReportPost)).all()

    def create(self, report:ReportPostData) -> ReportPost:
        """create reported post"""
        db_report = ReportPost.model_validate(report)
        db_session_value_create(session=self.db_session, value=db_report)
        return db_report
    
    def delete(self, db_report:ReportPost) -> None:
        """delete reported post"""
        self.db_session.delete(db_report)
        self.db_session.commit()