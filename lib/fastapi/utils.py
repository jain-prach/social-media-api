import pytz

from src.setup.config.settings import settings

def get_default_timezone():
    """get tz value for str timezone"""
    return pytz.timezone(settings.TIMEZONE)