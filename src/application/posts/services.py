import uuid
from typing import List, Optional

from sqlmodel import Session

from src.domain.posts.services import PostService
from src.interface.posts.schemas import PostSchema
from src.application.users.users.services import UserAppService
from src.application.users.services import BaseUserAppService
from src.domain.models import Post, BaseUser, User
from lib.fastapi.custom_exceptions import NotFoundException
from lib.fastapi.error_string import get_post_not_found, get_user_not_found
from lib.fastapi.custom_enums import FilterDates
from src.infrastructure.file_upload.services import Boto3Service
from src.infrastructure.email_service.services import SendgridService
from src.setup.config.settings import settings
from lib.fastapi.utils import get_random_values_from_list


class ReportedPostEmailService(SendgridService):
    """service to send email for reported post"""

    def send_email_for_reported_post(self, user: BaseUser):
        """sends reported post deleted information to the user"""
        self._send_template_email(
            sender=settings.REPORT_EMAIL_SENDER,
            receivers=[
                {
                    "email": user.email,
                    "name": user.user.username if user.user else "User",
                }
            ],
            template_id=settings.REPORT_POST_DELETE_TEMPLATE,
        )


class PostNotificationEmailService(SendgridService):
    """service to send email for post notification"""

    def send_email_for_post_notification(self, user: User, post_ids: List[uuid.UUID]):
        """send email for post notifications"""
        print(user.base_user.email)
        self._send_template_email(
            sender=settings.POST_NOTIFICATION_SENDER,
            receivers=[{"email": user.base_user.email, "name": user.username}],
            template_id=settings.POST_NOTIFICATION_TEMPLATE,
            template_dict={"post_ids": post_ids},
        )


class PostAppService:
    """handle post application services"""

    def __init__(self, session: Session):
        self.db_session = session
        self.post_service = PostService(session=self.db_session)

    def get_post_by_id(self, id: uuid.UUID) -> Optional[Post]:
        """get post using post id"""
        post = self.post_service.get_post_by_id(id=id)
        if not post:
            # raise NotFoundException(get_post_not_found())
            return None
        return post

    def get_all_posts_by_user_id(self, user_id: uuid.UUID) -> List[Post]:
        """get all posts posted by the user"""
        return self.post_service.get_all_posts_by_user_id(user_id=user_id)

    def get_all_posts_by_username(
        self,
        current_user_id: uuid.UUID,
        username: str,
        search: Optional[str],
        filter_by: Optional[FilterDates],
    ) -> List[Post]:
        """get all posts by username"""
        user_app_service = UserAppService(session=self.db_session)
        user = user_app_service.get_user_by_username(username=username)
        if not user:
            raise NotFoundException(get_user_not_found())
        user_app_service.check_private_user(current_user_id=current_user_id, user=user)
        return self.post_service.get_all_posts_by_user_id(
            user_id=user.id, search=search, filter_by=filter_by
        )

    def get_post_by_post_id_for_user(
        self, post_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Post]:
        """get post by post_id from user's post"""
        post = self.get_post_by_id(id=post_id)
        if not post or post.posted_by != user_id:
            # raise NotFoundException(get_post_not_found())
            return None
        return post

    def get_all_posts_not_liked_by_user(self, user_id: uuid.UUID) -> List[Post] | None:
        """get all posts not liked by user and posted from public users or user following"""
        user_app_service = UserAppService(session=self.db_session)
        user = user_app_service.get_user_by_id(id=user_id)
        public_users = user_app_service.get_all_public_users()
        if not user:
            return None
        return self.post_service.get_all_posts_not_liked_by_user(
            user=user, public_users=public_users
        )

    def create_post(self, post: PostSchema) -> Post:
        """create new post"""
        db_post = self.post_service.create(post=post)
        return db_post

    def update_post(self, post_id: uuid.UUID, post: PostSchema) -> Post:
        """update post"""
        db_post = self.get_post_by_post_id_for_user(
            post_id=post_id, user_id=post.posted_by
        )
        if not db_post:
            raise NotFoundException(get_post_not_found())
        return self.post_service.update(post=post, db_post=db_post)

    def delete_post(self, db_post: Post) -> None:
        """delete post"""
        # delete from minio
        for file in db_post.media:
            Boto3Service().delete_file(object_key=file.media_url)
        self.post_service.delete(db_post=db_post)

    def delete_post_by_user(self, post_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """delete post if user owns the post"""
        db_post = self.get_post_by_post_id_for_user(post_id=post_id, user_id=user_id)
        if not db_post:
            return None
        self.delete_post(db_post)

    def delete_post_by_admin(self, post_id: uuid.UUID) -> None:
        """delete post by post_id"""
        db_post = self.get_post_by_id(id=post_id)
        if not db_post:
            # return None
            raise NotFoundException(get_post_not_found())
        # send email to post owners
        base_user_app_service = BaseUserAppService(session=self.db_session)
        base_user = base_user_app_service.get_base_user_by_user_id(
            user_id=db_post.posted_by
        )
        if not base_user:
            raise NotFoundException(get_user_not_found())
        ReportedPostEmailService().send_email_for_reported_post(user=base_user)
        self.delete_post(db_post)

    def get_posts_to_schedule(self, user_id: uuid.UUID) -> List[uuid.UUID]:
        """get randomly selected posts to schedule"""
        posts = self.get_all_posts_not_liked_by_user(user_id=user_id)
        random_post_ids = get_random_values_from_list(
            var_list=[post.id for post in posts], count=settings.POST_COUNT_TO_NOTIFY
        )
        return random_post_ids

    def send_posts_in_email(self, user: User, post_ids: List[uuid.UUID]) -> None:
        """
        send posts in email service
        `Args`
            user:
                user to send email to
            post_ids:
                posts to share with the user
        """
        PostNotificationEmailService().send_email_for_post_notification(user=user, post_ids=post_ids)
