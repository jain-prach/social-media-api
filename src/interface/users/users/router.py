from typing import Annotated

from fastapi import APIRouter, UploadFile, Depends
from starlette.status import HTTP_201_CREATED

from src.setup.config.database import SessionDep
from src.application.users.users.services import UserService
from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from .schemas import UserWithBaseUserId, UserWithProfile, UserResponseData
from lib.fastapi.utils import get_valid_image_formats_list
from lib.fastapi.custom_exceptions import CustomValidationError
from lib.fastapi.error_string import get_invalid_file_type

router = APIRouter(
    prefix="/users", tags=["users"], route_class=UniqueConstraintErrorRoute
)


@router.post(
    "/create/",
    status_code=HTTP_201_CREATED,
    response_model=UserResponseData,
)
def create_user(user: Annotated[UserWithBaseUserId, Depends(UserWithBaseUserId)], profile: UploadFile, session: SessionDep):
    """create user for site access"""
    user_service = UserService(session)
    # check file type, upload profile, have object_key, save object_key
    if profile.content_type not in get_valid_image_formats_list():
        raise CustomValidationError(
            get_invalid_file_type(valid_types=get_valid_image_formats_list())
        )
    object_key = f"profiles/{user.base_user_id}/{profile.filename}"
    user_service.upload_profile_using_boto3(
        object_key=object_key, file=profile.file, file_type=profile.content_type
    )
    user = UserWithProfile(**user.model_dump(), profile=object_key)
    db_user = user_service.create_user(user)
    
    return {
        "message": "New user created",
        "success": True,
        "data": dict(**db_user.model_dump()),
    }
