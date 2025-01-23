from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from fastapi_pagination import Page, set_page, paginate, Params

from src.setup.config.database import SessionDep
from src.interface.auth.dependencies import AuthDep
from lib.fastapi.utils import check_id, check_file_type, get_valid_post_formats_list
from lib.fastapi.custom_enums import FilterDates
from src.application.posts.services import PostAppService
from src.application.payments.subscription.services import SubscriptionAppService
from .schemas import (
    PostSchema,
    PostResponseData,
    PostDeleteResponseData,
    PostListResponseData,
    PostResponse,
)
from .media.utils import handle_media_file_upload
from .utils import check_permission_to_post
from src.setup.config.settings import settings

router = APIRouter(prefix="/post", tags=["posts"])


@router.get("s/{username}/", status_code=HTTP_200_OK, response_model=PostListResponseData)
def list_post(
    current_user: AuthDep,
    username: str,
    session: SessionDep,
    page: int = 1,
    search: Optional[str] = None,
    filter_by: Optional[FilterDates] = None,
):
    """list all posts by username, admin has permission to access all private and public account posts"""
    post_app_service = PostAppService(session=session)
    posts = post_app_service.get_all_posts_by_username(
        current_user=current_user,
        username=username,
        search=search,
        filter_by=filter_by,
    )
    set_page(Page[PostResponse])
    paginated_response = paginate(
        sequence=[post for post in posts],
        params=Params(page=page, size=settings.POST_PAGINATION_SIZE),
    )
    return dict(data=paginated_response)


@router.post("/", status_code=HTTP_201_CREATED, response_model=PostResponseData)
def create_post(
    current_user: AuthDep,
    session: SessionDep,
    caption: Optional[str] = Form(None),
    media: List[UploadFile] = File(...),
):
    """create post created by current user"""

    user = check_permission_to_post(current_user=current_user, session=session)

    for file in media:
        # check file type
        check_file_type(
            content_type=file.content_type, valid_types=get_valid_post_formats_list()
        )

    # create post
    post = PostSchema(posted_by=user.id, caption=caption)
    post_app_service = PostAppService(session=session)
    db_post = post_app_service.create_post(post=post)
    post_id = db_post.id
    # handle media file upload for posts
    handle_media_file_upload(
        user_id=user.id, post_id=post_id, media=media, session=session
    )
    db_post = post_app_service.get_post_by_id(id=post_id)
    return dict(data=db_post)


@router.put("/{id}/", status_code=HTTP_200_OK, response_model=PostResponseData)
def update_post(current_user: AuthDep, session: SessionDep, id:str, caption:Optional[str]=Form(None)):
    """update post by current user (only caption)"""
    user = check_permission_to_post(current_user=current_user, session=session)
    post_id = check_id(id=id)
    post = PostSchema(caption=caption, posted_by=user.id)
    post_app_service = PostAppService(session=session)
    db_post = post_app_service.update_post(post_id=post_id, post=post)
    return dict(data=db_post)


@router.delete("/{id}/", status_code=HTTP_200_OK, response_model=PostDeleteResponseData)
def delete_post(current_user: AuthDep, id: str, session: SessionDep):
    """delete post by current user"""
    user = check_permission_to_post(current_user=current_user, session=session)
    post_id = check_id(id=id)
    post_app_service = PostAppService(session=session)
    post_app_service.delete_post_by_user(post_id=post_id, user_id=user.id)
    return {}

@router.post("/ad/", status_code=HTTP_201_CREATED, response_model=PostResponseData)
def create_ad(
    current_user: AuthDep,
    session: SessionDep,
    caption: Optional[str] = Form(None),
    media: List[UploadFile] = File(...),
):
    """create post created by current user"""

    user = check_permission_to_post(current_user=current_user, session=session)
    subscription_app_service = SubscriptionAppService(session=session)
    subscription_app_service.check_if_user_paid(user=user)
    for file in media:
        # check file type
        check_file_type(
            content_type=file.content_type, valid_types=get_valid_post_formats_list()
        )

    # create post
    post = PostSchema(posted_by=user.id, caption=caption)
    post_app_service = PostAppService(session=session)
    db_post = post_app_service.create_post(post=post)
    post_id = db_post.id
    # handle media file upload for posts
    handle_media_file_upload(
        user_id=user.id, post_id=post_id, media=media, session=session
    )
    db_post = post_app_service.get_post_by_id(id=post_id)
    return dict(data=db_post)
