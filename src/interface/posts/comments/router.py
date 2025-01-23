from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from .schemas import CommentPostSchema, CommentPost, CommentPostResponseData, CommentDeleteResponseData
from src.application.posts.comments.services import CommentAppService
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.utils import check_id
from ..utils import check_permission_to_post

router = APIRouter(prefix="/comment", tags=["posts"], route_class=UniqueConstraintErrorRoute)

@router.post("/{post_id}/", status_code=HTTP_200_OK, response_model=CommentPostResponseData)
def comment_post(current_user:AuthDep, post_id:str, post:CommentPostSchema, session:SessionDep):
    """comment on post by post_id"""
    user = check_permission_to_post(current_user=current_user, session=session)
    comment_app_service = CommentAppService(session=session)
    comment = CommentPost(commented_by=user.id, comment=post.comment, post_id=check_id(id=post_id))
    db_comment = comment_app_service.comment_post(comment=comment)
    return {"data": db_comment}

@router.delete("/", status_code=HTTP_200_OK, response_model=CommentDeleteResponseData)
def delete_comment(current_user:AuthDep, comment_id:str, session:SessionDep):
    """delete comment using comment_id"""
    comment_id=check_id(id=comment_id)
    user = check_permission_to_post(current_user=current_user, session=session)
    comment_app_service = CommentAppService(session=session)
    comment_app_service.remove_comment(commented_by=user.id, comment_id=comment_id)
    return {}