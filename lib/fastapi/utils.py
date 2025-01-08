import pytz
import random

from src.setup.config.settings import settings

def get_default_timezone():
    """get tz value for str timezone"""
    return pytz.timezone(settings.TIMEZONE)

def generate_otp():
    """returns a random 4 digit otp"""
    return random.randrange(1000, 9999)