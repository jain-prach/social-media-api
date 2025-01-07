import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings
from pydantic_extra_types.timezone_name import TimeZoneName 

load_dotenv("env/.env")


class Config(BaseSettings):
    """secrets and constants from env file to use in the codebase"""
    TIMEZONE:TimeZoneName = os.getenv("TIMEZONE")
    DB_ENGINE:str = os.getenv("DB_ENGINE")
    DB_NAME:str = os.getenv("DB_NAME")
    DB_USER:str = os.getenv("DB_USER")
    DB_PASSWORD:str = os.getenv("DB_PASSWORD")
    DB_HOST:str = os.getenv("DB_HOST")
    DB_PORT:str = os.getenv("DB_PORT")

    DATABASE_URL: str = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    STRONG_PASSWORD_PATTERN:str = r"^(?=\S*?[A-Z])(?=\S*?[a-z])(?=\S*?[0-9])(?=\S*?[!@#$%^&~`\\\/<>?\-_\+=\|])\S{8,}$"


settings = Config()