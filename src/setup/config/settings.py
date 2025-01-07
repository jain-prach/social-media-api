import os
from dotenv import load_dotenv
import pytz
from pytz.tzinfo import DstTzInfo

from pydantic_settings import BaseSettings

load_dotenv("env/.env")


class Config(BaseSettings):
    """secrets and constants from env file to use in the codebase"""

    TIMEZONE: DstTzInfo = pytz.timezone(os.getenv("TIMEZONE"))


settings = Config()
