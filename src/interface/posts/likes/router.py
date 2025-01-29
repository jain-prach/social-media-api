from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.interface.auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from .schemas import LikePost, LikePostResponseData, LikeDeleteResponseData
from src.application.posts.likes.services import LikeAppService
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.utils import check_id
from ..utils import check_permission_to_post

router = APIRouter(prefix="/like", tags=["posts"], route_class=UniqueConstraintErrorRoute)

@router.get("/{post_id}/", status_code=HTTP_200_OK, response_model=LikePostResponseData)
def like_post(current_user:AuthDep, post_id:str, session:SessionDep):
    """like post by post_id"""
    user = check_permission_to_post(current_user=current_user, session=session)
    like_app_service = LikeAppService(session=session)
    like = LikePost(liked_by=user.id, post_id=check_id(id=post_id))
    like_app_service.like_post(like=like)
    return {}

@router.delete("/{post_id}/", status_code=HTTP_200_OK, response_model=LikeDeleteResponseData)
def remove_like(current_user:AuthDep, post_id:str, session:SessionDep):
    """remove like from the post"""
    user = check_permission_to_post(current_user=current_user, session=session)
    like_app_service = LikeAppService(session=session)
    like = LikePost(liked_by=user.id, post_id=check_id(id=post_id))
    like_app_service.remove_like(like=like)
    return {}