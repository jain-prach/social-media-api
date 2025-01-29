from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from .schemas import ReportPostSchema, ReportPostData, ReportPostResponseData
from src.application.posts.reported_posts.services import ReportPostAppService
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.utils import check_id
from ..utils import check_permission_to_post

router = APIRouter(prefix="/report-post", tags=["posts"], route_class=UniqueConstraintErrorRoute)


@router.post(
    "/{post_id}/", status_code=HTTP_200_OK, response_model=ReportPostResponseData
)
def report_post(
    current_user: AuthDep, post_id: str, post: ReportPostSchema, session: SessionDep
):
    """report post by post_id"""
    user = check_permission_to_post(current_user=current_user, session=session)
    report_app_service = ReportPostAppService(session=session)
    report = ReportPostData(
        reported_by=user.id,
        reason=post.reason,
        additional_text=post.additional_text,
        post_id=check_id(id=post_id),
    )
    report_app_service.report_post(report)
    return {}
