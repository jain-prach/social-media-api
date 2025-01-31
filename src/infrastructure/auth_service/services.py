from datetime import datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from lib.fastapi.error_string import get_invalid_token
from lib.fastapi.custom_exceptions import UnauthorizedException
from src.setup.config.settings import settings
from lib.fastapi.utils import get_default_timezone


class JWTService:
    """services for jwt token handling"""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(JWTService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.secret_key = settings.JWT_SECRET_KEY
        self.algo = settings.JWT_ALGORITHM

    def encode(self, data: dict) -> str:
        """encode data to receive access token"""
        return jwt.encode(payload=data, key=self.secret_key, algorithm=self.algo)

    def encode_refresh(self, data: dict) -> str:
        """encode data to receive refresh token"""
        return jwt.encode(
            payload=data, key=settings.JWT_REFRESH_SECRET, algorithm=self.algo
        )

    def decode(self, token: str):
        """decode access token to verify login"""
        try:
            return jwt.decode(
                jwt=token, key=self.secret_key, algorithms=settings.JWT_ALGORITHM
            )
        except InvalidTokenError:
            raise UnauthorizedException(get_invalid_token())

    def decode_refresh(self, token: str):
        """decode refresh token to generate new access token"""
        try:
            return jwt.decode(
                jwt=token,
                key=settings.JWT_REFRESH_SECRET,
                algorithms=settings.JWT_ALGORITHM,
            )
        except InvalidTokenError:
            raise UnauthorizedException(get_invalid_token())
        
    def create_token(self, data: dict, expire:datetime) -> str:
        data_to_encode = data.copy()
        data_to_encode.update(
            {
                "exp": expire
            }
        )
        encoded_jwt = self.encode(data=data_to_encode)
        return encoded_jwt

    def create_access_token(self, data: dict) -> str:
        """create access token with expire time"""
        expire = datetime.now(tz=get_default_timezone()) + timedelta(**settings.ACCESS_TOKEN_LIFETIME)
        encoded_jwt = self.create_token(data=data, expire=expire)
        return encoded_jwt
    
    def create_otp_token(self, data: dict) -> str:
        """create otp token with otp expire time"""
        expire = datetime.now(tz=get_default_timezone()) + timedelta(**settings.OTP_EXPIRE_TIME)
        encoded_jwt = self.create_token(data=data, expire=expire)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """create refresh token with payload, expire time is set by default"""
        data_to_encode = data.copy()
        data_to_encode.update(
            {
                "exp": datetime.now(tz=get_default_timezone())
                + timedelta(**settings.REFRESH_TOKEN_LIFETIME)
            }
        )
        encoded_jwt = self.encode_refresh(data=data_to_encode)
        return encoded_jwt

    def generate_access_token_from_refresh_token(self, token: str):
        """generate access token from refresh token value"""
        payload = self.decode_refresh(token=token)
        access_token = self.create_access_token(data=payload)
        return access_token
