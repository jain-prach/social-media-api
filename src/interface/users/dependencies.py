from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.users.services import JWTService

class CustomHTTPBearer(HTTPBearer):
    """custom http bearer to return user role when authenticated"""
    def __init__(self):
        super().__init__(auto_error=True)

    async def __call__(self, request: Request) -> dict:
        token = await super().__call__(request)
        payload = JWTService().decode(token.credentials)
        return payload
    
http_bearer = CustomHTTPBearer()
AuthDep = Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]