from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from starlette_csrf import CSRFMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import Receive, Scope, Send
from starlette.datastructures import URL, Headers
from pydantic import ValidationError

from .custom_exceptions import (
    CustomException,
    UnauthorizedException,
    NotFoundException,
    ForbiddenException,
    BadRequestException,
    CustomValidationError,
    CustomUniqueConstraintError,
)
from .utils import get_pydantic_error_response


class CustomResponseCSRFMiddleware(CSRFMiddleware):
    """custom response for csrf token error"""

    def _get_error_response(self, request: Request) -> Response:
        return JSONResponse(
            status_code=403,
            content={
                "message": "CSRF token verification failed",
                "success": False,
                "data": {"message": "CSRF token verification failed"},
            },
        )


class CustomTrustedHostMiddleware(TrustedHostMiddleware):
    """custom response for trusted host error"""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.allow_any or scope["type"] not in (
            "http",
            "websocket",
        ):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        host = headers.get("host", "").split(":")[0]
        is_valid_host = False
        found_www_redirect = False
        for pattern in self.allowed_hosts:
            if host == pattern or (
                pattern.startswith("*") and host.endswith(pattern[1:])
            ):
                is_valid_host = True
                break
            elif "www." + host == pattern:
                found_www_redirect = True

        if is_valid_host:
            await self.app(scope, receive, send)
        else:
            response: Response
            if found_www_redirect and self.www_redirect:
                url = URL(scope=scope)
                redirect_url = url.replace(netloc="www." + url.netloc)
                response = RedirectResponse(url=str(redirect_url))
            else:
                response = JSONResponse(
                    status_code=400,
                    content={
                        "message": "Invalid host header",
                        "success": False,
                        "data": {"message": "Invalid host header"},
                    },
                )
            await response(scope, receive, send)


class HandleExceptionMiddleware(BaseHTTPMiddleware):
    """handling exception response"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
            return response
        except ValidationError as e:
            return get_pydantic_error_response(e)
        except (
            UnauthorizedException,
            NotFoundException,
            ForbiddenException,
            BadRequestException,
            CustomValidationError,
            CustomUniqueConstraintError,
            CustomException,
        ) as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "message": e.detail,
                    "success": False,
                    "data": {"message": e.detail},
                },
            )
        except Exception as e:
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": f"{e}",
                    "success": False,
                    "data": {"message": str(e)},
                },
            )
