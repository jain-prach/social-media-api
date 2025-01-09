import pytz
import random
import uuid

from lib.fastapi.custom_exceptions import CustomValidationError
from lib.fastapi.error_string import incorrect_id

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
        raise CustomValidationError(incorrect_id())