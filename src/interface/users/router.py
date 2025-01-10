from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from .schemas import GetBaseUser, BaseUserResponseData, BaseUserListResponseData, UpdateBaseUser, DeleteBaseUserResponseData
from ..auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from src.application.users.services import BaseUserAppService
from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_exceptions import NotFoundException, ForbiddenException
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.error_string import get_user_not_found, get_no_permission
from lib.fastapi.utils import check_id, only_admin_access


router = APIRouter(prefix="/base_user", tags=["base-user"], route_class=UniqueConstraintErrorRoute)

@router.get("s/", status_code=HTTP_200_OK, response_model=BaseUserListResponseData)
def list_users(current_user:AuthDep, session:SessionDep):
    """list all base users"""
    base_user_app_service = BaseUserAppService(session)
    if current_user.get("role") != Role.ADMIN.value:
        users = [base_user_app_service.get_base_user_by_id(id=current_user.get("id"))]
    else:
        users = base_user_app_service.get_all_base_users()
    return {"data": users}

@router.get(
    "/{id}/",
    status_code=HTTP_200_OK,
    response_model=BaseUserResponseData,
)
def get_user(
    current_user: AuthDep,
    data: Annotated[GetBaseUser, Depends(GetBaseUser)],
    session: SessionDep,
):
    """access base user details by id - only Admin access"""
    base_user_app_service = BaseUserAppService(session)
    
    only_admin_access(current_user=current_user)

    data.id = check_id(id=data.id)
    user = base_user_app_service.get_base_user_by_id(id=data.id)
    
    if not user:
        raise NotFoundException(get_user_not_found())

    return {
        "message": "User Information",
        "success": True,
        "data": dict(**user.model_dump()),
    }


### ME ROUTERS UPDATE
# @router.get("/me", status_code=HTTP_200_OK, response_model=BaseUserResponseData)
# def get_own_user(current_user:AuthDep, session:SessionDep):
#     """access own user details"""
#     id = current_user.get("id")
#     user = BaseUserAppService(session=session).get_base_user_by_id(id=id)
#     return {
#         "message": "Own Details",
#         "success": True,
#         "data": dict(**user.model_dump()),
#     }

# @router.get("/me/", status_code=HTTP_200_OK, response_model=UserResponseData)
# def get_own_user(current_user: AuthDep, session: SessionDep):
#     """get own user details"""
#     id = current_user.get("id")
#     user = BaseUserAppService(session=session).get_base_user_by_id(id=id)
#     if user.role == Role.USER:
#         if not user.user:
#             raise NotFoundException(get_user_to_create())
#         db_user = user.user
#     else:
#         if not user.admin:
#             raise NotFoundException(get_admin_to_create())
#         db_user = user.admin
#     return {"message": "Own Details View", "data": {**db_user.model_dump()}}


@router.put("/{id}/", status_code=HTTP_200_OK, response_model=BaseUserResponseData)
def update_user(
    current_user: AuthDep,
    user: UpdateBaseUser,
    session: SessionDep
):
    """update existing user"""
    id = check_id(id=user.id)
    base_user_app_service = BaseUserAppService(session)

    if current_user.get("role") == Role.USER.value:
        if id != current_user.get("id"):
            raise ForbiddenException(get_no_permission())  
        
    db_user = base_user_app_service.update_base_user(user=user)

    return {
        "message": "New user updated",
        "success": True,
        "data": dict(**db_user.model_dump()),
    }

@router.delete("/{id}/", status_code=HTTP_200_OK, response_model=DeleteBaseUserResponseData)
def delete_user(current_user: AuthDep, id: str, session: SessionDep):
    """delete existing user"""
    id = check_id(id=id)
    only_admin_access(current_user=current_user)
    BaseUserAppService(session).delete_base_user(id=id)
    return DeleteBaseUserResponseData()