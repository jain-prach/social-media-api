from fastapi import UploadFile

from lib.fastapi.utils import check_file_type, get_valid_image_formats_list
from src.application.users.users.services import UserAppService
from .schemas import UserWithBaseUserId, UserWithProfile


def handle_user_create_with_profile_upload(
    user: UserWithBaseUserId, profile: UploadFile
):
    # check file type
    check_file_type(
        content_type=profile.content_type, valid_types=get_valid_image_formats_list()
    )
    # create object_key and upload profile
    object_key = UserAppService.handle_profile_upload(profile=profile, user=user)
    # save object_key with the user
    user = UserWithProfile(**user.model_dump(), profile=object_key)
    return user
