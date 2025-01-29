from typing import Annotated
import uuid

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from .schemas import GetBaseUser, BaseUserResponseData, BaseUserListResponseData, DeleteBaseUserResponseData
from ..auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from src.application.users.services import BaseUserAppService
from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_exceptions import NotFoundException
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.error_string import get_user_not_found
from lib.fastapi.utils import check_id, only_admin_access


router = APIRouter(prefix="/base-user", tags=["base-user"], route_class=UniqueConstraintErrorRoute)

@router.get("s/", status_code=HTTP_200_OK, response_model=BaseUserListResponseData)
def list_base_users(current_user:AuthDep, session:SessionDep):
    """list all base users"""
    base_user_app_service = BaseUserAppService(session)
    if current_user.get("role") != Role.ADMIN.value:
        users = [base_user_app_service.get_base_user_by_id(id=uuid.UUID(current_user.get("id")))]
    else:
        users = base_user_app_service.get_all_base_users()
    return {"data": users}

@router.get(
    "/{id}/",
    status_code=HTTP_200_OK,
    response_model=BaseUserResponseData,
)
def get_base_user(
    current_user: AuthDep,
    data: Annotated[GetBaseUser, Depends(GetBaseUser)],
    session: SessionDep,
):
    """access base user details by id - only Admin access"""
    only_admin_access(current_user=current_user)
    base_user_app_service = BaseUserAppService(session)
    data.id = check_id(id=str(data.id))
    user = base_user_app_service.get_base_user_by_id(id=data.id)
    if not user:
        raise NotFoundException(get_user_not_found())
    return {
        "message": "User Information",
        "success": True,
        "data": user,
    }


@router.get("/get/me/", status_code=HTTP_200_OK, response_model=BaseUserResponseData)
def get_own_details(current_user:AuthDep, session:SessionDep):
    """access own user details"""
    user_id = check_id(id=current_user.get("id"))
    base_user_service = BaseUserAppService(session=session)
    user = base_user_service.get_base_user_by_id(id=user_id)
    return {
        "message": "Own Details",
        "success": True,
        "data": user,
    }


# @router.put("/{id}/", status_code=HTTP_200_OK, response_model=BaseUserResponseData)
# def update_user(
#     current_user: AuthDep,
#     user: UpdateBaseUser,
#     session: SessionDep
# ):
#     """update existing user"""
#     only_admin_access(current_user=current_user)
#     base_user_app_service = BaseUserAppService(session)

#     #ONLY ROLE UPDATE SHOULDN'T BE ACCESSIBLE TO USER
#     # id = check_id(id=user.id)
#     # if current_user.get("role") == Role.USER.value:
#     #     if id != check_id(current_user.get("id")):
#     #         raise ForbiddenException(get_no_permission())  
        
#     db_user = base_user_app_service.update_base_user(user=user)

#     return {
#         "message": "New user updated",
#         "success": True,
#         "data": db_user,
#     }

@router.delete("/{id}/", status_code=HTTP_200_OK, response_model=DeleteBaseUserResponseData)
def delete_base_user(current_user: AuthDep, id: str, session: SessionDep):
    """delete existing user"""
    id = check_id(id=id)
    only_admin_access(current_user=current_user)
    BaseUserAppService(session).delete_base_user(id=id)
    return {}