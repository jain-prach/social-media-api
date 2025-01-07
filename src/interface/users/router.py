from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED

from .schemas import BaseUserResponse

router = APIRouter(tags=["base-user"])


@router.get(
    "/register/",
    status_code=HTTP_201_CREATED,
    response_model=BaseUserResponse
)
def register():
    pass
