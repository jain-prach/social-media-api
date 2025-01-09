from typing import Optional
import http

from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_409_CONFLICT
)


class CustomException(Exception):
    """
    custom exception for API

    Attributes
        status_code: Optional[int]
            response status code that defines error
        detail: Optional[str]
            any details regarding the error 
    """
    def __init__(
        self,
        status_code: Optional[int] = HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail if detail else http.HTTPStatus(status_code).phrase


class UnauthorizedException(CustomException):
    """raise unauthorized exception"""
    def __init__(self, detail: Optional[str] = None) -> None:
        status_code = HTTP_401_UNAUTHORIZED
        super().__init__(status_code, detail)


class NotFoundException(CustomException):
    """raise not found exception"""
    def __init__(self, detail: Optional[str] = None) -> None:
        status_code = HTTP_404_NOT_FOUND
        super().__init__(status_code, detail)


class BadRequestException(CustomException):
    """raise bad request exception"""
    def __init__(self, detail: Optional[str] = None) -> None:
        status_code = HTTP_400_BAD_REQUEST
        super().__init__(status_code, detail)


class ForbiddenException(CustomException):
    """raise forbidden exception"""
    def __init__(self, detail: Optional[str] = None) -> None:
        status_code = HTTP_403_FORBIDDEN
        super().__init__(status_code, detail)

class CustomValidationError(CustomException):
    """raise custom validation errors"""
    def __init__(self, detail: str = None) -> None:
        status_code = HTTP_422_UNPROCESSABLE_ENTITY
        super().__init__(status_code, detail)

class CustomUniqueConstraintError(CustomException):
    """raise custom unique constraint errors"""
    def __init__(self, detail: str = None) -> None:
        status_code = HTTP_409_CONFLICT
        super().__init__(status_code, detail)