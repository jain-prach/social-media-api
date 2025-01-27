from typing import Annotated, Optional
import uuid

from fastapi import APIRouter, UploadFile, Depends, File, Form
from starlette.status import HTTP_200_OK

from src.setup.config.database import SessionDep
from src.application.users.users.services import UserAppService
from src.interface.auth.dependencies import AuthDep
from .schemas import (
    UserWithBaseUserId,
    UserResponseData,
    GetUser,
    DeleteUserResponseData,
    UserListResponseData,
)
from .utils import handle_user_create_with_profile_upload
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.utils import check_id, only_own_access, only_user_access
from lib.fastapi.custom_exceptions import (
    NotFoundException,
)
from lib.fastapi.custom_enums import Role, ProfileType
from lib.fastapi.error_string import (
    get_user_not_found,
)

router = APIRouter(
    prefix="/user", tags=["users"], route_class=UniqueConstraintErrorRoute
)


@router.get("s/", status_code=HTTP_200_OK, response_model=UserListResponseData)
def list_users(current_user: AuthDep, session: SessionDep):
    """list all base users"""
    user_app_service = UserAppService(session)
    if current_user.get("role") != Role.ADMIN.value:
        users = [
            user_app_service.get_user_by_base_user_id(
                base_user_id=uuid.UUID(current_user.get("id"))
            )
        ]
    else:
        users = user_app_service.get_all_users()
    return {"data": users}


# NOT NEEDED because dummy user is created while registration
# @router.post(
#     "/create/",
#     status_code=HTTP_201_CREATED,
#     response_model=UserResponseData,
# )
# def create_user(
#     current_user: AuthDep,
#     session: SessionDep,
#     user: Annotated[UserWithBaseUserId, Depends(UserWithBaseUserId)],
#     profile: Optional[UploadFile] = File(None),
# ):
#     """create user for site access"""
#     user.base_user_id = check_id(user.base_user_id)
#     if current_user.get("role") != Role.ADMIN.value:
#         only_own_access(current_user=current_user, id=user.base_user_id)

#     user_app_service = UserAppService(session)
#     base_user = BaseUserAppService(session=session).get_base_user_by_id(
#         id=user.base_user_id
#     )
#     if not base_user:
#         raise NotFoundException(get_user_not_found())
#     if base_user.role == Role.ADMIN:
#         raise BadRequestException(get_admin_to_not_create_user())
#     if base_user.user:
#         raise CustomValidationError(get_user_created())

#     if profile:
#         handle_user_create_with_profile_upload(user=user, profile=profile)

#     db_user = user_app_service.create_user(user)

#     return {
#         "message": "New user created",
#         "success": True,
#         "data": dict(**db_user.model_dump()),
#     }


@router.get("/{username}/", status_code=HTTP_200_OK, response_model=UserResponseData)
def get_user(
    current_user: AuthDep, data: Annotated[GetUser, Depends()], session: SessionDep
):
    """get user details by username"""
    # only_admin_access(current_user=current_user)
    user = UserAppService(session=session).get_user_by_username(username=data.username)
    if not user:
        raise NotFoundException(get_user_not_found())
    return {"message": "User Details", "data": user}


@router.put("/", status_code=HTTP_200_OK, response_model=UserResponseData)
def update_user(
    current_user: AuthDep,
    session: SessionDep,
    username: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_type: ProfileType = Form(ProfileType.PUBLIC),
    profile: Optional[UploadFile] = File(None),
):
    """update your own user details"""
    # role = current_user.get("role")
    # user.base_user_id = check_id(user.base_user_id)

    # if role != Role.ADMIN.value:
    #     only_own_access(current_user=current_user, id=user.base_user_id)
    only_user_access(current_user=current_user)
    user_app_service = UserAppService(session=session)
    db_user = user_app_service.get_user_by_base_user_id(base_user_id=check_id(id=current_user.get("id")))

    user = UserWithBaseUserId(
        username=username if username else db_user.username,
        bio=bio if bio else db_user.bio,
        profile_type=profile_type,
        base_user_id=db_user.base_user_id,
    )

    if profile and profile != "":
        user = handle_user_create_with_profile_upload(user=user, profile=profile)

    db_user = user_app_service.update_user(user=user)

    return {
        "message": "User Updated!",
        "data": db_user,
    }


@router.delete("/{base_user_id}/", status_code=HTTP_200_OK, response_model=DeleteUserResponseData)
def delete_user(current_user: AuthDep, base_user_id: str, session: SessionDep):
    """delete existing user"""
    id = check_id(id=base_user_id)
    if current_user.get("role") != Role.ADMIN.value:
        only_own_access(current_user=current_user, access_id=id)
    UserAppService(session).delete_user(base_user_id=id)
    return {}
