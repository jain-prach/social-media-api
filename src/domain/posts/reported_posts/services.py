from sqlmodel import Session

from .models import ReportPost
from src.interface.posts.reported_posts.schemas import ReportPostData
from lib.fastapi.utils import db_session_value_create

class ReportPostService:
    """handle database operations for reporting a post"""
    def __init__(self, session:Session):
        self.db_session = session

    def create(self, report:ReportPostData) -> ReportPost:
        """create report on post"""
        db_report = ReportPost.model_validate(report)
        db_session_value_create(session=self.db_session, value=db_report)
        return db_report