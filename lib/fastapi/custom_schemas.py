from typing import Optional, List

from pydantic import BaseModel

class BaseResponseSchema(BaseModel):
    """base response schema"""

    message: Optional[str] = "success"
    success: Optional[bool] = True

class BaseResponseNoDataSchema(BaseResponseSchema):
    """base response schema with data value none"""
    data:List = []
