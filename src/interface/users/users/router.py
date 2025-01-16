from typing import Annotated, Optional
import uuid

from fastapi import APIRouter, UploadFile, Depends, File
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from src.setup.config.database import SessionDep
from src.application.users.users.services import UserAppService
from src.application.users.services import BaseUserAppService
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
from lib.fastapi.utils import check_id, only_own_access
from lib.fastapi.custom_exceptions import (
    NotFoundException,
    BadRequestException,
    CustomValidationError,
)
from lib.fastapi.custom_enums import Role
from lib.fastapi.error_string import (
    get_user_not_found,
    get_admin_to_not_create_user,
    get_user_created,
    get_user_not_created,
)

router = APIRouter(
    prefix="/user", tags=["users"], route_class=UniqueConstraintErrorRoute
)


@router.get("s/", status_code=HTTP_200_OK, response_model=UserListResponseData)
def list_users(current_user: AuthDep, session: SessionDep):
    """list all base users"""
    user_app_service = UserAppService(session)
    if current_user.get("role") != Role.ADMIN.value:
        users = [user_app_service.get_user_by_base_user_id(base_user_id=uuid.UUID(current_user.get("id")))]
    else:
        users = user_app_service.get_all_users()
    return {"data": users}


@router.post(
    "/create/",
    status_code=HTTP_201_CREATED,
    response_model=UserResponseData,
)
def create_user(
    current_user: AuthDep,
    session: SessionDep,
    user: Annotated[UserWithBaseUserId, Depends(UserWithBaseUserId)],
    profile: Optional[UploadFile] = File(None),
):
    """create user for site access"""
    user.base_user_id = check_id(user.base_user_id)
    user_app_service = UserAppService(session)
    if current_user.get("role") != Role.ADMIN.value:
        only_own_access(current_user=current_user, id=user.base_user_id)

    base_user = BaseUserAppService(session=session).get_base_user_by_id(
        id=user.base_user_id
    )
    if not base_user:
        raise NotFoundException(get_user_not_found())
    if base_user.role == Role.ADMIN:
        raise BadRequestException(get_admin_to_not_create_user())
    if base_user.user:
        raise CustomValidationError(get_user_created())

    if profile:
        handle_user_create_with_profile_upload(user=user, profile=profile)

    db_user = user_app_service.create_user(user)

    return {
        "message": "New user created",
        "success": True,
        "data": dict(**db_user.model_dump()),
    }


@router.get("/{id}/", status_code=HTTP_200_OK, response_model=UserResponseData)
def get_user(
    current_user: AuthDep, data: Annotated[GetUser, Depends()], session: SessionDep
):
    """get user details by username"""
    # only_admin_access(current_user=current_user)
    user = UserAppService(session=session).get_user_by_username(username=data.username)
    if not user:
        raise NotFoundException(get_user_not_found())
    return {"message": "User Details", "data": {**user.model_dump()}}


@router.put("/{id}/", status_code=HTTP_200_OK, response_model=UserResponseData)
def update_user(
    current_user: AuthDep,
    session: SessionDep,
    user: Annotated[UserWithBaseUserId, Depends(UserWithBaseUserId)],
    profile: Optional[UploadFile] = File(None),
):
    """update user details"""
    role = current_user.get("role")
    user.base_user_id = check_id(user.base_user_id)
    user_app_service = UserAppService(session=session)

    if role != Role.ADMIN.value:
        only_own_access(current_user=current_user, id=user.base_user_id)

    # get user
    db_user = user_app_service.get_user_by_base_user_id(base_user_id=user.base_user_id)
    if not user:
        raise CustomValidationError(get_user_not_created())

    if profile:
        user = handle_user_create_with_profile_upload(user=user, profile=profile)

    db_user = user_app_service.update_user(user=user, db_user=db_user)

    return {
        "message": "User Updated!",
        "data": dict(**db_user.model_dump()),
    }


@router.delete("/{id}/", status_code=HTTP_200_OK, response_model=DeleteUserResponseData)
def delete_user(current_user: AuthDep, base_user_id: str, session: SessionDep):
    """delete existing user"""
    id = check_id(id=base_user_id)
    if current_user.get("role") != Role.ADMIN.value:
        only_own_access(current_user=current_user, id=id)
    UserAppService(session).delete_user(base_user_id=id)
    return DeleteUserResponseData()
