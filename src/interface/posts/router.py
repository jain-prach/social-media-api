from typing import List, Annotated, Optional

from fastapi import APIRouter, UploadFile, Depends
from starlette.status import HTTP_201_CREATED, HTTP_200_OK
from fastapi_pagination import Page, set_page, paginate, Params

from src.setup.config.database import SessionDep
from src.interface.auth.dependencies import AuthDep
from lib.fastapi.utils import check_id, check_file_type, get_valid_post_formats_list
from src.application.posts.services import PostAppService
from .schemas import CreatePostSchema, PostSchema, PostResponseData, UpdatePostSchema, PostDeleteResponseData, PostListResponseData, PostResponse
from .media.utils import handle_media_file_upload
from .utils import check_permission_to_post
from src.setup.config.settings import settings

router = APIRouter(prefix="/post", tags=["posts"])

@router.get("s/", status_code=HTTP_200_OK, response_model=PostListResponseData)
def list_post(current_user:AuthDep, username:str, session:SessionDep, page:int=1, search:Optional[str]=None):
    """list all posts by username, admin has permission to access all private and public account posts"""
    current_user_id = check_id(id=current_user.get("id"))
    post_app_service = PostAppService(session=session)
    posts = post_app_service.get_all_posts_by_username(current_user_id=current_user_id, username=username, search=search)
    set_page(Page[PostResponse])
    paginated_response = paginate(sequence=[post for post in posts], params=Params(page=page, size=settings.POST_PAGINATION_SIZE))
    return dict(data=paginated_response)

@router.post('/create/', status_code=HTTP_201_CREATED, response_model=PostResponseData)
def create_post(current_user:AuthDep, post:Annotated[CreatePostSchema, Depends()], media:List[UploadFile], session:SessionDep):
    """create post created by current user"""
    
    user = check_permission_to_post(current_user=current_user, session=session)

    for file in media:
        # check file type
        check_file_type(
            content_type=file.content_type, valid_types=get_valid_post_formats_list()
        )
    
    #create post
    post = PostSchema(posted_by=user.id, caption=post.caption)
    post_app_service = PostAppService(session=session)
    db_post = post_app_service.create_post(post=post)
    post_id = db_post.id
    #handle media file upload for posts
    handle_media_file_upload(user_id=user.id, post_id=post_id, media=media, session=session)
    db_post = post_app_service.get_post_by_id(id=post_id)
    return dict(data=db_post)

@router.put('/{id}/', status_code=HTTP_200_OK, response_model=PostResponseData)
def update_post(current_user:AuthDep, post:UpdatePostSchema, session:SessionDep):
    """update post by current user (only caption)"""
    user = check_permission_to_post(current_user=current_user, session=session)
    post_id = check_id(id=post.id)
    post = PostSchema(caption=post.caption, posted_by=user.id)
    db_post = PostAppService(session=session).update_post(post_id=post_id, post=post)
    return dict(data=db_post)

@router.delete('/{id}/', status_code=HTTP_200_OK, response_model=PostDeleteResponseData)
def delete_post(current_user:AuthDep, id:str, session:SessionDep):
    """delete post by current user"""
    user = check_permission_to_post(current_user=current_user, session=session)
    post_id = check_id(id=id)
    PostAppService(session=session).delete_post(post_id=post_id, user_id=user.id)
    return PostDeleteResponseData()