from datetime import datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from lib.fastapi.error_string import get_invalid_token
from lib.fastapi.custom_exceptions import UnauthorizedException
from src.setup.config.settings import settings

class JWTService:
    """services for jwt token handling"""
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(JWTService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.secret_key = settings.JWT_SECRET_KEY
        self.algo = settings.JWT_ALGORITHM

    def encode(self, data:dict) -> str:
        """encode data to receive access token"""
        return jwt.encode(payload=data, key=self.secret_key, algorithm=self.algo)

    def decode(self, token:str):
        """decode access token to verify login"""
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)
        except InvalidTokenError:
            raise UnauthorizedException(get_invalid_token())

    def create_access_token(self, data:dict) -> str:
        """create access token with expire time"""
        data_to_encode = data.copy()
        expire = datetime.now() + timedelta(**settings.ACCESS_TOKEN_LIFETIME)
        data_to_encode.update({"exp": expire})
        encoded_jwt = self.encode(data=data_to_encode)
        return encoded_jwt