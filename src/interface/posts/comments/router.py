from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from .schemas import CommentPostSchema, CommentPost
from src.application.posts.comments.services import CommentAppService
from lib.fastapi.custom_schemas import BaseResponseNoDataSchema
from lib.fastapi.utils import check_id
from ..utils import check_permission_to_post

router = APIRouter(prefix="/comment", tags=["posts"])

@router.post("/{post_id}/", status_code=HTTP_200_OK, response_model=BaseResponseNoDataSchema)
def comment_post(current_user:AuthDep, post:CommentPostSchema, session:SessionDep):
    """comment on post by post_id"""
    user = check_permission_to_post(current_user=current_user, session=session)
    comment_app_service = CommentAppService(session=session)
    comment = CommentPost(commented_by=user.id, comment=post.comment, post_id=check_id(id=post.post_id))
    comment_app_service.comment_post(comment)
    return {"message": "Commented on post!"}