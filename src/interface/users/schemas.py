from pydantic import BaseModel

class GetBaseUser(BaseModel):
    """information required to get base user"""
    id: str