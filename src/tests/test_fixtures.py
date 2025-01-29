from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import uuid

import pytest
from sqlmodel import Session, select
from fastapi import UploadFile

from src.domain.models import (
    BaseUser,
    Otp,
    User,
    Post,
    Media,
    FollowersModel,
    Admin,
    ReportPost,
)
from .test_data import (
    create_user,
    create_admin,
    create_public_user,
    create_private_user,
)
from src.application.users.services import PasswordService, JWTService
from .test_utils import create_value_using_session
from src.setup.config.settings import settings
from src.infrastructure.file_upload.services import Boto3Service
from lib.fastapi.custom_enums import StatusType, ProfileType, ReportReason


@pytest.fixture(scope="function")
def before_create_base_user() -> BaseUser:
    def create_base_user(session: Session, user_dict: dict):
        user_dict["password"] = PasswordService().get_hashed_password(
            user_dict["password"]
        )
        db_user = BaseUser.model_validate(user_dict)
        create_value_using_session(session=session, value=db_user)
        return db_user

    return create_base_user


@pytest.fixture(scope="function")
def before_create_otp(before_create_base_user):
    def create_otp(session: Session):
        user = before_create_base_user(session=session, user_dict=create_user())
        db_otp = Otp.model_validate({"base_user_id": user.id})
        create_value_using_session(session=session, value=db_otp)
        return db_otp

    return create_otp


@pytest.fixture(scope="function")
def before_create_otp_token(before_create_otp):
    def create_otp_token(session: Session):
        otp = before_create_otp(session=session)
        otp_token = JWTService().create_access_token(
            data={"id": str(otp.base_user.id), "otp": otp.otp},
            expire=datetime.now() + timedelta(**settings.OTP_EXPIRE_TIME),
        )
        return otp_token

    return create_otp_token


@pytest.fixture(scope="function")
def before_create_base_user_admin() -> BaseUser:
    def create_base_user(session: Session, user_dict: dict):
        user_dict["password"] = PasswordService().get_hashed_password(
            user_dict["password"]
        )
        db_user = BaseUser.model_validate(user_dict)
        create_value_using_session(session=session, value=db_user)
        return db_user

    return create_base_user


@pytest.fixture(scope="function")
def before_admin_login_cred(before_create_base_user) -> str:
    def admin_login_cred(session: Session):
        db_base_user = before_create_base_user(
            session=session, user_dict=create_admin()
        )
        db_admin = Admin.model_validate({"base_user_id": db_base_user.id})
        create_value_using_session(session=session, value=db_admin)
        login_token = JWTService().create_access_token(
            data={"id": str(db_base_user.id), "role": db_base_user.role.value},
            expire=datetime.now() + timedelta(**settings.ACCESS_TOKEN_LIFETIME),
        )
        return login_token

    return admin_login_cred


@pytest.fixture(scope="function")
def before_user_login_cred(before_create_base_user) -> str:
    def user_login_cred(session: Session):
        db_base_user = before_create_base_user(session=session, user_dict=create_user())
        login_token = JWTService().create_access_token(
            data={"id": str(db_base_user.id), "role": db_base_user.role.value},
            expire=datetime.now() + timedelta(**settings.ACCESS_TOKEN_LIFETIME),
        )
        return login_token

    return user_login_cred


@pytest.fixture(scope="function")
def before_create_normal_user(before_create_base_user) -> str:
    def create_normal_user_fixture(session: Session, user_dict: dict):
        db_base_user = before_create_base_user(session=session, user_dict=create_user())
        with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
            profile = UploadFile(f)
            object_key = f"profiles/{db_base_user.id}/{db_base_user.id}.jpeg"
            boto3_service = Boto3Service()
            boto3_service.upload_file_from_memory(
                object_key=object_key,
                file_content=profile.file,
                file_type="image/jpeg",
            )
            db_user = User.model_validate(
                {**user_dict, "profile": object_key, "base_user_id": db_base_user.id}
            )
            create_value_using_session(session=session, value=db_user)
        return db_user

    return create_normal_user_fixture


@pytest.fixture(scope="function")
def before_create_public_user_login_cred(before_create_normal_user):
    def create_public_user_login_cred(session: Session):
        db_user = before_create_normal_user(
            session=session, user_dict=create_public_user()
        )
        login_token = JWTService().create_access_token(
            data={
                "id": str(db_user.base_user.id),
                "role": db_user.base_user.role.value,
            },
            expire=datetime.now() + timedelta(**settings.ACCESS_TOKEN_LIFETIME),
        )
        return login_token

    return create_public_user_login_cred


@pytest.fixture(scope="function")
def before_create_private_user_login_cred(before_create_normal_user):
    def create_private_user_login_cred(session: Session):
        db_user = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        login_token = JWTService().create_access_token(
            data={
                "id": str(db_user.base_user.id),
                "role": db_user.base_user.role.value,
            },
            expire=datetime.now() + timedelta(**settings.ACCESS_TOKEN_LIFETIME),
        )
        return login_token

    return create_private_user_login_cred


@pytest.fixture(scope="function")
def before_create_post(before_create_normal_user):
    def create_post(session: Session, user_dict: dict):
<<<<<<< HEAD
        db_user = session.scalars(select(User).where(User.username == user_dict["username"])).first()
=======
        db_user = session.scalars(
            select(User).where(User.username == user_dict["username"])
        ).first()
>>>>>>> db81b47e93c4576a973deb70e666e05a70868fe3
        if not db_user:
            db_user = before_create_normal_user(session=session, user_dict=user_dict)
        db_post = Post.model_validate(
            {"posted_by": db_user.id, "caption": "caption text"}
        )
        create_value_using_session(session=session, value=db_post)
        with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
            media = [
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
            ]
            for i, file in enumerate(media):
                get_file_extension = str(file.filename).split(".")[-1]
                # create object_key and upload media
                object_key = (
                    f"posts/{db_user.id}/{db_post.id}/post_{i}.{get_file_extension}"
                )
                boto3_service = Boto3Service()
                boto3_service.upload_file_from_memory(
                    object_key=object_key,
                    file_content=file.file,
                    file_type="image/jpeg",
                )
                db_media = Media.model_validate(
                    {
                        "post_id": db_post.id,
                        "media_url": object_key,
                        "media_type": "image/jpeg",
                    }
                )
                # save urls and types to media
                create_value_using_session(session=session, value=db_media)
        return db_post
    return create_post

@pytest.fixture(scope="function")
def before_create_post_with_different_timestamp(before_create_normal_user):
    def create_post(session: Session, user_dict: dict):
        db_user = session.scalars(select(User).where(User.username == user_dict["username"])).first()
        if not db_user:
            db_user = before_create_normal_user(session=session, user_dict=user_dict)
        db_post = Post.model_validate(
            {"posted_by": db_user.id, "caption": "caption text", "created_at":datetime.now()-relativedelta(months=1)}
        )
        create_value_using_session(session=session, value=db_post)
        with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
            media = [
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
            ]
            for i, file in enumerate(media):
                get_file_extension = str(file.filename).split(".")[-1]
                # create object_key and upload media
                object_key = (
                    f"posts/{db_user.id}/{db_post.id}/post_{i}.{get_file_extension}"
                )
                boto3_service = Boto3Service()
                boto3_service.upload_file_from_memory(
                    object_key=object_key,
                    file_content=file.file,
                    file_type="image/jpeg",
                )
                db_media = Media.model_validate(
                    {
                        "post_id": db_post.id,
                        "media_url": object_key,
                        "media_type": "image/jpeg",
                    }
                )
                # save urls and types to media
                create_value_using_session(session=session, value=db_media)
        return db_post
    return create_post

@pytest.fixture(scope="function")
def before_create_post_caption_search(before_create_normal_user):
    def create_post(session: Session, user_dict: dict):
        db_user = session.scalars(select(User).where(User.username == user_dict["username"])).first()
        if not db_user:
            db_user = before_create_normal_user(session=session, user_dict=user_dict)
        db_post = Post.model_validate(
            {"posted_by": db_user.id, "caption": "search"}
        )
        create_value_using_session(session=session, value=db_post)
        with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
            media = [
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
            ]
            for i, file in enumerate(media):
                get_file_extension = str(file.filename).split(".")[-1]
                # create object_key and upload media
                object_key = (
                    f"posts/{db_user.id}/{db_post.id}/post_{i}.{get_file_extension}"
                )
                boto3_service = Boto3Service()
                boto3_service.upload_file_from_memory(
                    object_key=object_key,
                    file_content=file.file,
                    file_type="image/jpeg",
                )
                db_media = Media.model_validate(
                    {
                        "post_id": db_post.id,
                        "media_url": object_key,
                        "media_type": "image/jpeg",
                    }
                )
                # save urls and types to media
                create_value_using_session(session=session, value=db_media)
        return db_post
    return create_post


@pytest.fixture(scope="function")
def before_create_post_with_different_timestamp(before_create_normal_user):
    def create_post(session: Session, user_dict: dict):
        db_user = session.scalars(
            select(User).where(User.username == user_dict["username"])
        ).first()
        if not db_user:
            db_user = before_create_normal_user(session=session, user_dict=user_dict)
        db_post = Post.model_validate(
            {
                "posted_by": db_user.id,
                "caption": "caption text",
                "created_at": datetime.now() - relativedelta(months=1),
            }
        )
        create_value_using_session(session=session, value=db_post)
        with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
            media = [
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
            ]
            for i, file in enumerate(media):
                get_file_extension = str(file.filename).split(".")[-1]
                # create object_key and upload media
                object_key = (
                    f"posts/{db_user.id}/{db_post.id}/post_{i}.{get_file_extension}"
                )
                boto3_service = Boto3Service()
                boto3_service.upload_file_from_memory(
                    object_key=object_key,
                    file_content=file.file,
                    file_type="image/jpeg",
                )
                db_media = Media.model_validate(
                    {
                        "post_id": db_post.id,
                        "media_url": object_key,
                        "media_type": "image/jpeg",
                    }
                )
                # save urls and types to media
                create_value_using_session(session=session, value=db_media)
        return db_post

    return create_post


@pytest.fixture(scope="function")
def before_create_post_caption_search(before_create_normal_user):
    def create_post(session: Session, user_dict: dict):
        db_user = session.scalars(
            select(User).where(User.username == user_dict["username"])
        ).first()
        if not db_user:
            db_user = before_create_normal_user(session=session, user_dict=user_dict)
        db_post = Post.model_validate({"posted_by": db_user.id, "caption": "search"})
        create_value_using_session(session=session, value=db_post)
        with open("src/tests/test_files/spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg", "rb") as f:
            media = [
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
                UploadFile(f, filename="spcode-0SXyYNDUt6b9WEPHQqqw4L.jpeg"),
            ]
            for i, file in enumerate(media):
                get_file_extension = str(file.filename).split(".")[-1]
                # create object_key and upload media
                object_key = (
                    f"posts/{db_user.id}/{db_post.id}/post_{i}.{get_file_extension}"
                )
                boto3_service = Boto3Service()
                boto3_service.upload_file_from_memory(
                    object_key=object_key,
                    file_content=file.file,
                    file_type="image/jpeg",
                )
                db_media = Media.model_validate(
                    {
                        "post_id": db_post.id,
                        "media_url": object_key,
                        "media_type": "image/jpeg",
                    }
                )
                # save urls and types to media
                create_value_using_session(session=session, value=db_media)
        return db_post

    return create_post


@pytest.fixture(scope="function")
def before_create_follow_request():
    def create_follow_request(
        session: Session, follower_id: uuid.UUID, following_id: uuid.UUID
    ):
        db_following = session.get(User, following_id)
        db_follow = FollowersModel.model_validate(
            {
                "follower_id": follower_id,
                "following_id": following_id,
                "status": StatusType.PENDING
                if db_following.profile_type == ProfileType.PRIVATE.value
                else StatusType.APPROVED,
            }
        )
        create_value_using_session(session=session, value=db_follow)
        return db_follow

    return create_follow_request


@pytest.fixture(scope="function")
def before_create_approved_follow_requests(before_create_normal_user):
    def create_follow_request(
        session: Session, follower_id: uuid.UUID, following_id: uuid.UUID
    ):
        db_follow = FollowersModel.model_validate(
            {
                "follower_id": follower_id,
                "following_id": following_id,
                "status": StatusType.APPROVED,
            }
        )
        create_value_using_session(session=session, value=db_follow)
        return db_follow

    return create_follow_request


# @pytest.fixture(scope="function")
# def before_create_approved_following(before_create_normal_user):
#     def create_follow_request(
#         session: Session, follower_id: uuid.UUID, user:User
#     ):
#         db_follow = FollowersModel.model_validate(
#             {
#                 "follower_id": follower_id,
#                 "following_id": user.id,
#                 "status": StatusType.APPROVED,
#             }
#         )
#         create_value_using_session(session=session, value=db_follow)
#         return db_follow
#     return create_follow_request


@pytest.fixture(scope="function")
def before_create_private_user_with_followers(
    before_create_normal_user, before_create_approved_follow_requests
):
    def create_private_user_with_followers(session: Session):
        user = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        username = user.username
        user2 = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        before_create_approved_follow_requests(
            session=session, follower_id=user2.id, following_id=user.id
        )
        return username

    return create_private_user_with_followers


@pytest.fixture(scope="function")
def before_create_public_user_with_followers(
    before_create_normal_user, before_create_approved_follow_requests
):
    def create_public_user_with_followers(session: Session):
        user = before_create_normal_user(
            session=session, user_dict=create_public_user()
        )
        username = user.username
        user2 = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        before_create_approved_follow_requests(
            session=session, follower=user2.id, following_id=user.id
        )
        return username

    return create_public_user_with_followers


@pytest.fixture(scope="function")
def before_create_private_user_with_following(
    before_create_normal_user, before_create_approved_follow_requests
):
    def create_private_user_with_following(session: Session):
        user = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        username = user.username
        user2 = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        before_create_approved_follow_requests(
            session=session, follower_id=user.id, following_id=user2.id
        )
        return username

    return create_private_user_with_following


@pytest.fixture(scope="function")
def before_create_public_user_with_following(
    before_create_normal_user, before_create_approved_follow_requests
):
    def create_public_user_with_following(session: Session):
        user = before_create_normal_user(
            session=session, user_dict=create_public_user()
        )
        username = user.username
        user2 = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        before_create_approved_follow_requests(
            session=session, follower_id=user.id, following_id=user2.id
        )
        return username

    return create_public_user_with_following


@pytest.fixture(scope="function")
def before_create_follow(
    before_create_normal_user, before_create_approved_follow_requests
):
    def create_follow(session: Session):
        user1 = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        user2 = before_create_normal_user(
            session=session, user_dict=create_private_user()
        )
        db_follow = before_create_approved_follow_requests(
            session=session, follower_id=user1.id, following_id=user2.id
        )
        return db_follow

    return create_follow


@pytest.fixture(scope="function")
def before_report_post(before_create_normal_user, before_create_post):
    def report_post(session: Session, posted_by: dict, reported_by: dict):
        post = before_create_post(session=session, user_dict=posted_by)
        user = session.scalars(
            select(User).where(User.username == reported_by["username"])
        ).first()
        if not user:
            user = before_create_normal_user(session=session, user_dict=reported_by)
        db_report = ReportPost.model_validate(
            {
                "reported_by": user.id,
                "post_id": post.id,
                "reason": ReportReason.COPYRIGHT,
                "additional_text": "not null value",
            }
        )
        create_value_using_session(session=session, value=db_report)
        return db_report
    return report_post
