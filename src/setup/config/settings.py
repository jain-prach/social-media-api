import os
import ast

from dotenv import load_dotenv

from pydantic_settings import BaseSettings
from pydantic_extra_types.timezone_name import TimeZoneName 
from pydantic import EmailStr

load_dotenv("env/.env")


class Config(BaseSettings):
    """secrets and constants from env file to use in the codebase"""
    BASE_URL:str = os.getenv("BASE_URL")
    TIMEZONE:TimeZoneName = os.getenv("TIMEZONE")

    DB_ENGINE:str = os.getenv("DB_ENGINE")
    DB_NAME:str = os.getenv("DB_NAME")
    DB_USER:str = os.getenv("DB_USER")
    DB_PASSWORD:str = os.getenv("DB_PASSWORD")
    DB_HOST:str = os.getenv("DB_HOST")
    DB_PORT:str = os.getenv("DB_PORT")
    TEST_DB_NAME:str = os.getenv("TEST_DB_NAME")

    DATABASE_URL: str = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    TEST_DATABASE_URL:str = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

    STRONG_PASSWORD_PATTERN:str = r"^(?=\S*?[A-Z])(?=\S*?[a-z])(?=\S*?[0-9])(?=\S*?[!@#$%^&~`\\\/<>?\-_\+=\|])\S{8,}$"
    VALID_USERNAME_PATTERN:str = r"^[A-Za-z0-9_\.]{3,32}$"

    JWT_SECRET_KEY:str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM:str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_LIFETIME:dict = ast.literal_eval(os.getenv("ACCESS_TOKEN_EXPIRATION"))

    SENDGRID_API_KEY:str = os.getenv("SENDGRID_API_KEY")
    FORGOT_PASSWORD_TEMPLATE:str = os.getenv("FORGOT_PASSWORD_TEMPLATE")
    SENDGRID_SENDER:EmailStr = os.getenv("SENDGRID_SENDER")

    OTP_EXPIRE_TIME:dict = ast.literal_eval(os.getenv("OTP_EXPIRE_TIME"))

    CELERY_BACKEND_URL:str = os.getenv("CELERY_BACKEND_URL")
    CELERY_BROKER_URL:str = os.getenv("CELERY_BROKER_URL")

    GIT_CLIENT_ID:str = os.getenv("GIT_CLIENT_ID")
    GIT_REDIRECT_URI:str = f"{BASE_URL}git-callback/"
    GIT_CLIENT_SECRET:str = os.getenv("GIT_CLIENT_SECRET")
    GIT_TOKEN_URL:str = os.getenv("GIT_TOKEN_URL")
    GIT_API_URL:str = os.getenv("GIT_API_URL")
    
    AWS_S3_ENDPOINT_URL:str = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_BUCKET_NAME:str = os.getenv("AWS_BUCKET_NAME")
    AWS_ACCESS_KEY_ID:str = os.getenv("AWS_ACCESS_KEY")
    AWS_SECRET_KEY_ID:str = os.getenv("AWS_SECRET_KEY")
    AWS_S3_REGION_NAME:str = os.getenv("AWS_S3_REGION_NAME")
    PRESIGNED_URL_TIME:dict = ast.literal_eval(os.getenv("PRESIGNED_URL_TIME"))

    POST_PAGINATION_SIZE:int = int(os.getenv("POST_PAGINATION_SIZE"))


settings = Config()