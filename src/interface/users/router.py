from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.status import HTTP_200_OK

from .schemas import GetBaseUser
from ..auth.dependencies import AuthDep
from ..auth.schemas import BaseUserResponseData
from src.setup.config.database import SessionDep
from src.application.users.services import UserService
from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_exceptions import NotFoundException
from lib.fastapi.error_string import get_user_not_found
from lib.fastapi.utils import check_id


router = APIRouter(tags=["base-user"])

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
    """access user details by id"""
    # ASK: accepts gibberish data when current_user has role user and returns current_user details
    user_service = UserService(session)

    if current_user.get("role") == Role.ADMIN:
        data.id = check_id(id=data.id)
        user = user_service.get_user_by_id(id=data.id)
    elif current_user.get("role") == Role.USER:
        user = user_service.get_user_by_id(id=current_user.get("id"))
    else:
        user = None

    if not user:
        raise NotFoundException(get_user_not_found())

    return {
        "message": "User Information View",
        "success": True,
        "data": dict(**user.model_dump()),
    }
