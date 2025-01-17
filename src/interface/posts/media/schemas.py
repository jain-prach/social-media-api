import uuid

from pydantic import BaseModel


class MediaSchema(BaseModel):
    """media schema with media url and type list"""

    post_id: uuid.UUID
    media_url: str
    media_type: str
