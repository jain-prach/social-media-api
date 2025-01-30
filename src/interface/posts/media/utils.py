from typing import List
import uuid

from fastapi import UploadFile
from sqlmodel import Session

from src.application.posts.media.services import MediaAppService
from .schemas import MediaSchema

def handle_media_file_upload(user_id:uuid.UUID, post_id:uuid.UUID, media:List[UploadFile], session:Session) -> None:
    """handle posts media files upload"""

    for i, file in enumerate(media):
        get_file_extension = str(file.filename).split(".")[-1]
        # create object_key and upload media
        object_key = f"posts/{user_id}/{post_id}/post_{i}.{get_file_extension}"
        MediaAppService.handle_media_upload(file=file, object_key=object_key)
        media_schema = MediaSchema(post_id=post_id, media_url=object_key, media_type=file.content_type)
        # save urls and types to media
        MediaAppService(session=session).create_media(media=media_schema)