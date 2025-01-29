from typing import Callable

from fastapi.routing import APIRoute
from fastapi import Request, Response
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from lib.fastapi.custom_exceptions import CustomUniqueConstraintError
from lib.fastapi.utils import get_unique_constraint_error
from lib.fastapi.error_string import (
    get_request_already_sent,
    get_post_already_liked,
    get_post_reported_once,
)


class UniqueConstraintErrorRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except IntegrityError as e:
                if isinstance(e.orig, UniqueViolation):
                    if hasattr(e.orig, "diag"):
                        unique_constraint = e.orig.diag.constraint_name
                        if unique_constraint == "RequestSent":
                            raise CustomUniqueConstraintError(
                                detail=get_request_already_sent()
                            )
                        elif unique_constraint == "LikedAlready":
                            raise CustomUniqueConstraintError(
                                detail=get_post_already_liked()
                            )
                        elif unique_constraint == "ReportedOnce":
                            raise CustomUniqueConstraintError(
                                detail=get_post_reported_once()
                            )
                raise CustomUniqueConstraintError(
                    detail=get_unique_constraint_error(error_message=str(e))
                )

        return custom_route_handler
