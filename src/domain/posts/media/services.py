from sqlmodel import Session

from src.interface.posts.media.schemas import MediaSchema
from lib.fastapi.utils import db_session_value_create
from .models import Media


class MediaService:
    """handle database tasks for media"""

    def __init__(self, session: Session):
        self.db_session = session

    def create_media(self, media: MediaSchema) -> Media:
        """create media query in the database"""
        db_media = Media.model_validate(media)
        db_session_value_create(session=self.db_session, value=db_media)
        return db_media
