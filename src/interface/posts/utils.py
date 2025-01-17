from sqlmodel import Session

from lib.fastapi.custom_enums import Role
from lib.fastapi.custom_exceptions import UnauthorizedException, NotFoundException
from lib.fastapi.error_string import get_admin_not_allowed, get_user_not_created
from lib.fastapi.utils import check_id
from src.application.users.users.services import UserAppService


def check_permission_to_post(current_user:dict, session:Session):
    """check if the user is allowed to post"""
    if current_user.get("role") == Role.ADMIN.value:
        raise UnauthorizedException(get_admin_not_allowed())
    
    user = UserAppService(session=session).get_user_by_base_user_id(base_user_id=check_id(current_user.get("id")))
    if not user:
        raise NotFoundException(get_user_not_created())
    return user