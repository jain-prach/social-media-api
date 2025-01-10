import uuid
from typing import Optional
from pydantic import BaseModel

from lib.fastapi.custom_schemas import BaseResponseSchema


class CreateAdmin(BaseModel):
    """create admin for base_user_id"""

    base_user_id: str | uuid.UUID


class AdminResponse(CreateAdmin):
    """admin response valid fields"""

    id: uuid.UUID


class AdminResponseData(BaseResponseSchema):
    """admin response data with data attribute to include AdminResponse"""

    data: AdminResponse


class DeleteAdminResponseData(BaseResponseSchema):
    """delete admin response with data attribute set to constant string value"""

    data: Optional[str] = "Admin Deleted!"
