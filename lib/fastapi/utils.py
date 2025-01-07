import pytz

from src.setup.config.settings import settings

def get_default_timezone():
    return pytz.timezone(settings.TIMEZONE)