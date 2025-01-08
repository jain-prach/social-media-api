from typing import Optional

from pydantic import BaseModel

class BaseResponseSchema(BaseModel):
    """base response schema"""

    message: Optional[str] = "success"
    success: Optional[bool] = True
