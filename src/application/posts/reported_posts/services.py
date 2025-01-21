from typing import Optional, List
import uuid

from sqlmodel import Session

from src.interface.posts.reported_posts.schemas import ReportPostData
from src.domain.posts.reported_posts.services import ReportPostService
from src.domain.models import ReportPost
from src.application.posts.services import PostAppService


class ReportPostAppService:
    """handling application services for reporting posts"""

    def __init__(self, session: Session):
        self.db_session = session
        self.report_post_service = ReportPostService(session=self.db_session)

    def get_reported_post_by_id(self, report_post_id:uuid.UUID) -> Optional[ReportPost]:
        """get reported post by id"""
        return self.report_post_service.get_reported_post_by_id(id=report_post_id)

    def get_all_reported_posts(self) -> List[ReportPost]:
        """get all reported posts"""
        return self.report_post_service.get_all_reported_posts()

    def report_post(self, report: ReportPostData) -> Optional[ReportPost]:
        """report post for post_id"""
        post_app_service = PostAppService(session=self.db_session)
        post = post_app_service.get_post_by_id(id=report.post_id)
        # reported_by_list = [report.reported_by for report in post.report] #and report.reported_by not in reported_by_list
        if post:
            return self.report_post_service.create(report=report)
        return None