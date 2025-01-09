from typing import Callable

from fastapi.routing import APIRoute
from fastapi import Request, Response
from sqlalchemy.exc import IntegrityError

from lib.fastapi.custom_exceptions import CustomUniqueConstraintError
class UniqueConstraintErrorRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except IntegrityError as e:
                raise CustomUniqueConstraintError(detail=f"Already Exists! Unique {str(e.orig).split("Key (")[1].split(")")[0]} is required!")
        return custom_route_handler