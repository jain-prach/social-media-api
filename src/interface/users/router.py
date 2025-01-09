from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from .schemas import GetBaseUser, BaseUserSchema, BaseUserResponseData, BaseUserListResponseData, DeleteBaseUserResponseData
from ..auth.dependencies import AuthDep
from src.setup.config.database import SessionDep
from src.application.users.services import BaseUserService
from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_exceptions import NotFoundException, ForbiddenException
from lib.fastapi.error_string import get_user_not_found, get_no_permission
from lib.fastapi.utils import check_id


router = APIRouter(tags=["base-user"])

@router.get("/users/", status_code=HTTP_200_OK, response_model=BaseUserListResponseData)
def list_users(current_user:AuthDep, session:SessionDep):
    """list all base users"""
    base_user_service = BaseUserService(session)
    if current_user.get("role") != Role.ADMIN.value:
        users = [base_user_service.get_user_by_id(id=current_user.get("id"))]
    users = base_user_service.get_all_base_users()
    return {"data": users}

@router.get(
    "/user/{id}/",
    status_code=HTTP_200_OK,
    response_model=BaseUserResponseData,
)
def get_user(
    current_user: AuthDep,
    data: Annotated[GetBaseUser, Depends(GetBaseUser)],
    session: SessionDep,
):
    """access base user details by id"""
    # ASK: accepts gibberish data when current_user has role user and returns current_user details
    base_user_service = BaseUserService(session)

    if current_user.get("role") == Role.ADMIN.value:
        data.id = check_id(id=data.id)
        user = base_user_service.get_user_by_id(id=data.id)
    elif current_user.get("role") == Role.USER.value:
        user = base_user_service.get_user_by_id(id=current_user.get("id"))
    else:
        user = None

    if not user:
        raise NotFoundException(get_user_not_found())

    return {
        "message": "User Information View",
        "success": True,
        "data": dict(**user.model_dump()),
    }

@router.put("/user/{id}/", status_code=HTTP_200_OK, response_model=BaseUserResponseData)
async def update_user(
    current_user: AuthDep,
    id: str, 
    user: BaseUserSchema,
    session: SessionDep
):
    """update existing user"""
    id = check_id(id=id)
    base_user_service = BaseUserService(session)

    if current_user.get("role") == Role.USER.value:
        if id != current_user.get("id"):
            raise ForbiddenException(get_no_permission())  
        
    db_user = base_user_service.update_user(id=id, user=user)

    return {
        "message": "New user updated",
        "success": True,
        "data": dict(**db_user.model_dump()),
    }

@router.delete("/user/{id}/", status_code=HTTP_200_OK, response_model=DeleteBaseUserResponseData)
async def delete_user(current_user: AuthDep, id: str, session: SessionDep):
    """delete existing user"""
    id = check_id(id=id)
    base_user_service = BaseUserService(session)
    
    if current_user.get("role") == Role.USER.value:
        raise ForbiddenException(get_no_permission())
    
    base_user_service.delete_user(id=id)
    return DeleteBaseUserResponseData()