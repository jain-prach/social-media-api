from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED

from .schemas import CreateBaseUser, BaseUserResponseData
from src.setup.config.database import SessionDep
from src.application.users.services import UserService
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute

router = APIRouter(tags=["base-user"], route_class=UniqueConstraintErrorRoute)


@router.post(
    "/register/", status_code=HTTP_201_CREATED, response_model=BaseUserResponseData
)
def register(user: CreateBaseUser, session: SessionDep):
    """create base user for site access"""
    db_user = UserService(session).create_user(user)
    return {
        "message": "New user created",
        "success": True,
        "data": dict(**db_user.model_dump()),
    }
