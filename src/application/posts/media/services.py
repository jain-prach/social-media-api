from fastapi import UploadFile
from sqlmodel import Session

from src.infrastructure.file_upload.services import Boto3Service
from src.domain.models import Media
from src.domain.posts.media.services import MediaService
from src.interface.posts.media.schemas import MediaSchema


class MediaAppService:
    """handle media application services"""

    def __init__(self, session: Session):
        self.db_session = session
        self.media_service = MediaService(session=self.db_session)

    def create_media(self, media: MediaSchema) -> Media:
        """create media"""
        return self.media_service.create_media(media=media)

    @staticmethod
    def handle_media_upload(file: UploadFile, object_key:str) -> None:
        """create object key and handle media upload"""
        Boto3Service().upload_file_from_memory(
            object_key=object_key, file_content=file.file, file_type=file.content_type
        )

    # def delete_media(self, media:Media) -> None:
    #     """delete media"""
    #     return self.media_service.delete_media(media=media)