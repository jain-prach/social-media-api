import pytz
import random
import uuid
from typing import List
from datetime import datetime
from dateutil.relativedelta import relativedelta

from sqlmodel import Session

from lib.fastapi.custom_enums import Role, FilterDates
from lib.fastapi.custom_exceptions import CustomValidationError, ForbiddenException
from lib.fastapi.error_string import (
    get_incorrect_id,
    get_no_permission,
    get_invalid_file_type,
)
from src.setup.config.settings import settings


def get_default_timezone():
    """get tz value for str timezone"""
    return pytz.timezone(settings.TIMEZONE)


def generate_otp():
    """returns a random 6 digit otp"""
    return random.randrange(100000, 999999)


def check_id(id: str) -> uuid.UUID:
    try:
        return uuid.UUID(id)
    except ValueError:
        raise CustomValidationError(get_incorrect_id())


def db_session_value_create(session: Session, value: dict):
    """helper function for repetitive database operation"""
    session.add(value)
    session.commit()
    session.refresh(value)


def get_valid_image_formats_list() -> List[str]:
    return ["image/jpeg", "image/png", "image/heic", "image/jpg"]

def get_valid_post_formats_list() -> List[str]:
    return ["image/jpeg", "image/png", "image/heic", "image/jpg", "video/mp4", "video/mpeg"]

def only_admin_access(current_user: dict) -> None:
    if current_user.get("role") == Role.USER.value:
        raise ForbiddenException(get_no_permission())


def only_own_access(current_user: dict, id: uuid.UUID) -> None:
    if uuid.UUID(current_user.get("id")) != id:
        raise ForbiddenException(get_no_permission())
    return None


def check_file_type(content_type: str, valid_types: List) -> None:
    if content_type not in valid_types:
        raise CustomValidationError(
            get_invalid_file_type(valid_types=valid_types)
        )

def get_after_date_from_enum(value:FilterDates) -> datetime:
    """get date value from today based on enum"""
    today = datetime.now(tz=get_default_timezone())
    if value == FilterDates.THIS_MONTH.value:
        delta = relativedelta(months=1)
    elif value == FilterDates.LAST_SIX_MONTHS.value:
        delta = relativedelta(months=6)
    elif value == FilterDates.LAST_ONE_YEAR.value:
        delta = relativedelta(years=1)
    else:
        delta = relativedelta(years=10)
    return today-delta