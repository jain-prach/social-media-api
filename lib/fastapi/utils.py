import pytz
import random
import uuid
from typing import List

from sqlmodel import Session

from lib.fastapi.custom_exceptions import CustomValidationError
from lib.fastapi.error_string import get_incorrect_id

from src.setup.config.settings import settings

def get_default_timezone():
    """get tz value for str timezone"""
    return pytz.timezone(settings.TIMEZONE)

def generate_otp():
    """returns a random 4 digit otp"""
    return random.randrange(1000, 9999)

def check_id(id:str) -> uuid.UUID:
    try:
        return uuid.UUID(id)
    except ValueError:
        raise CustomValidationError(get_incorrect_id())
    
def db_session_value_create(session:Session, value:dict):
    """helper function for repetitive database operation"""
    session.add(value)
    session.commit()
    session.refresh(value)

def get_valid_image_formats_list() -> List[str]:
    return ["image/jpeg", "image/png", "image/heic", "image/jpg"]