from fastapi.responses import JSONResponse
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
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
from .utils import get_pydantic_validation_error


class HandleExceptionMiddleware(BaseHTTPMiddleware):
    """handling exception response"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
            return response
        except ValidationError as e:
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": get_pydantic_validation_error(errors=e.errors()),
                    "success": False,
                    "data": {},
                },
            )
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
                content={"message": e.detail, "success": False, "data": {}},
            )
        except Exception as e:
            print("*****", e)
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"{e}", "success": False, "data": {}},
            )
