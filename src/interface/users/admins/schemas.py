import uuid
from typing import Optional
from pydantic import BaseModel

from lib.fastapi.custom_schemas import BaseResponseSchema, BaseResponseNoDataSchema


class CreateAdmin(BaseModel):
    """create admin for base_user_id"""

    base_user_id: str | uuid.UUID


class AdminResponse(CreateAdmin):
    """admin response valid fields"""

    id: uuid.UUID


class AdminResponseData(BaseResponseSchema):
    """admin response data with data attribute to include AdminResponse"""

    data: AdminResponse


class DeleteAdminResponseData(BaseResponseNoDataSchema):
    """delete admin response with message attribute set to constant string value"""

    message: Optional[str] = "Admin Deleted!"
