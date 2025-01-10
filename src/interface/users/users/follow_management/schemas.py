from pydantic import BaseModel


class SendRequestSchema(BaseModel):
    """send request to user"""

    username: str
