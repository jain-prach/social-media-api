from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED, HTTP_200_OK

from src.setup.config.database import SessionDep
from src.interface.auth.dependencies import AuthDep
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from lib.fastapi.utils import check_id, only_admin_access, only_own_access
from lib.fastapi.custom_exceptions import (
    NotFoundException,
    CustomValidationError,
)
from lib.fastapi.error_string import (
    get_user_not_found,
    get_admin_created
)
from .schemas import CreateAdmin, AdminResponseData, DeleteAdminResponseData
from src.application.users.admins.services import AdminAppService
from src.application.users.services import BaseUserAppService

router = APIRouter(
    prefix="/admin", tags=["admins"], route_class=UniqueConstraintErrorRoute
)


@router.post(
    "/create/",
    status_code=HTTP_201_CREATED,
    response_model=AdminResponseData,
)
def create_user(
    current_user: AuthDep,
    session: SessionDep,
    user: CreateAdmin,
):
    """create admin for site access"""
    user.base_user_id = check_id(user.base_user_id)

    only_admin_access(current_user=current_user)
    only_own_access(current_user=current_user, id=user.base_user_id)

    base_user = BaseUserAppService(session=session).get_base_user_by_id(
        id=user.base_user_id
    )
    if not base_user:
        raise NotFoundException(get_user_not_found())
    if base_user.admin:
        raise CustomValidationError(get_admin_created())

    db_user = AdminAppService(session).create_admin(user)

    return {
        "message": "Admin created",
        "success": True,
        "data": dict(**db_user.model_dump()),
    }


@router.get("/me/", status_code=HTTP_200_OK, response_model=AdminResponseData)
def get_user(
    current_user: AuthDep, session: SessionDep
):
    """get own admin details"""
    only_admin_access(current_user=current_user)
    id = check_id(current_user.get("id"))
    user = AdminAppService(session=session).get_admin_by_base_user_id(base_user_id=id)
    return {"message": "User Details", "data": {**user.model_dump()}}


@router.delete("/{id}/", status_code=HTTP_200_OK, response_model=DeleteAdminResponseData)
def delete_user(current_user: AuthDep, base_user_id: str, session: SessionDep):
    """delete existing user"""
    only_admin_access(current_user=current_user)
    id = check_id(id=base_user_id)
    only_own_access(current_user=current_user, id=id)
    AdminAppService(session).delete_admin(base_user_id=id)
    return DeleteAdminResponseData()