import uuid

from pydantic import BaseModel, field_serializer

from src.infrastructure.file_upload.services import Boto3Service


class MediaSchema(BaseModel):
    """media schema with media url and type list"""

    post_id: uuid.UUID
    media_url: str
    media_type: str

    @field_serializer('media_url')
    def serialize_media_url(self, media_url: str):
        if media_url:
            boto3_service = Boto3Service()
            presigned_url = boto3_service.get_presigned_url(object_key=media_url)
            return presigned_url
        return None
