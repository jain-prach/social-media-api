from typing import Annotated
from datetime import datetime

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from src.application.users.services import JWTService
from lib.fastapi.error_string import get_access_token_expired
from lib.fastapi.utils import get_default_timezone


class CustomHTTPBearer(HTTPBearer):
    """custom http bearer to return user role when authenticated"""

    def __init__(self):
        super().__init__()

    async def __call__(self, request: Request):
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        token = HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
        payload = JWTService().decode(token.credentials)
        if not payload.get("id") or not payload.get("role") or not payload.get("exp"):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if datetime.fromtimestamp(
            payload.get("exp"), tz=get_default_timezone()
        ) < datetime.now(tz=get_default_timezone()):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=get_access_token_expired(),
            )
        return payload


http_bearer = CustomHTTPBearer()
AuthDep = Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]
