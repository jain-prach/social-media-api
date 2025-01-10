from fastapi import APIRouter

from lib.fastapi.custom_routes import UniqueConstraintErrorRoute
from src.interface.auth.dependencies import AuthDep
from .schemas import SendRequestSchema


router = APIRouter(
    prefix="/follow", tags=["follow"], route_class=UniqueConstraintErrorRoute
)

@router.post("/send/")
def send_request(current_user:AuthDep, user:SendRequestSchema):
    """send request to mentioned user by username"""
    