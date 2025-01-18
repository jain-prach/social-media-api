from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from .schemas import LikePostSchema, LikePost
from src.application.posts.likes.services import LikeAppService
from lib.fastapi.custom_schemas import BaseResponseNoDataSchema
from lib.fastapi.utils import check_id
from ..utils import check_permission_to_post

router = APIRouter(prefix="/like", tags=["posts"])

@router.post("/{post_id}/", status_code=HTTP_200_OK, response_model=BaseResponseNoDataSchema)
def like_post(current_user:AuthDep, post:LikePostSchema, session:SessionDep):
    """like post by post_id"""
    user = check_permission_to_post(current_user=current_user, session=session)
    like_app_service = LikeAppService(session=session)
    like = LikePost(liked_by=user.id, post_id=check_id(id=post.post_id))
    like_app_service.like_post(like)
    return {"message": "Post Liked!"}