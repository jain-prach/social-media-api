from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from src.setup.config.database import SessionDep
from src.interface.auth.dependencies import AuthDep
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.utils import check_id, only_admin_access, only_own_access
from lib.fastapi.error_string import get_admin_not_created
from lib.fastapi.custom_exceptions import NotFoundException
from .schemas import AdminResponseData, DeleteAdminResponseData
from src.application.users.admins.services import AdminAppService

from src.interface.posts.reported_posts.schemas import ReportPostListResponseData, ReportPostDeletedResponseData
from src.application.posts.reported_posts.services import ReportPostAppService
from src.application.posts.services import PostAppService

router = APIRouter(
    prefix="/admin", tags=["admins"], route_class=UniqueConstraintErrorRoute
)

# NOT NEEDED: admin created automatically while registration
# @router.post(
#     "/create/",
#     status_code=HTTP_201_CREATED,
#     response_model=AdminResponseData,
# )
# def create_user(
#     current_user: AuthDep,
#     session: SessionDep,
#     user: CreateAdmin,
# ):
#     """create admin for site access"""
#     user.base_user_id = check_id(user.base_user_id)

#     only_admin_access(current_user=current_user)
#     only_own_access(current_user=current_user, id=user.base_user_id)

#     base_user = BaseUserAppService(session=session).get_base_user_by_id(
#         id=user.base_user_id
#     )
#     if not base_user:
#         raise NotFoundException(get_user_not_found())
#     if base_user.admin:
#         raise CustomValidationError(get_admin_created())

#     db_user = AdminAppService(session).create_admin(user)

#     return {
#         "message": "Admin created",
#         "success": True,
#         "data": dict(**db_user.model_dump()),
#     }


@router.get("/me/", status_code=HTTP_200_OK, response_model=AdminResponseData)
def get_admin(
    current_user: AuthDep, session: SessionDep
):
    """get own admin details"""
    only_admin_access(current_user=current_user)
    id = check_id(current_user.get("id"))
    admin_app_service = AdminAppService(session)
    admin = admin_app_service.get_admin_by_base_user_id(base_user_id=id)
    if not admin:
        raise NotFoundException(get_admin_not_created())
    return {"message": "Admin Details", "data": admin}


@router.delete("/{id}/", status_code=HTTP_200_OK, response_model=DeleteAdminResponseData)
def delete_admin(current_user: AuthDep, base_user_id: str, session: SessionDep):
    """delete existing admin"""
    only_admin_access(current_user=current_user)
    id = check_id(id=base_user_id)
    only_own_access(current_user=current_user, access_id=id)
    admin_app_service = AdminAppService(session)
    admin_app_service.delete_admin(base_user_id=id)
    return {}

###custom admin routers
@router.get("/reported_posts/", status_code=HTTP_200_OK, response_model=ReportPostListResponseData)
def get_reported_posts(current_user:AuthDep, session:SessionDep):
    """get list of all reported posts"""
    only_admin_access(current_user=current_user)
    report_post_app_service = ReportPostAppService(session=session)
    reported_posts = report_post_app_service.get_all_reported_posts()
    return {"data": reported_posts}

@router.delete("/reported_posts/{id}/", status_code=HTTP_200_OK, response_model=ReportPostDeletedResponseData)
def delete_reported_post(current_user:AuthDep, post_id:str, session:SessionDep):
    """delete reported post by getting post_id"""
    only_admin_access(current_user=current_user)
    post_app_service = PostAppService(session=session)
    post_app_service.delete_post_by_admin(post_id=check_id(id=post_id))
    return {}