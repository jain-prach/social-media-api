import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from pydantic import ValidationError
# from psycopg2.errors import ForeignKeyViolation

from src.tests.test_client import setup_database
from src.domain.users.users.follow_management.services import FollowService
from src.tests.test_utils import create_session
from src.tests.test_fixtures import (
    before_create_follow_request,
    before_create_approved_follow_requests,
    before_create_base_user,
    before_create_normal_user,
)
from src.tests.test_data import create_private_user
from lib.fastapi.custom_enums import StatusType
from src.domain.models import FollowersModel


def test_get_follow_by_follow_id(
    before_create_normal_user, before_create_follow_request
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    follow = FollowService(session=session).get_follow_by_follow_id(id=db_follow.id)
    assert db_follow == follow
    session.close()


def test_get_follow_by_follow_id_for_invalid_id():
    session = create_session()
    follow = FollowService(session=session).get_follow_by_follow_id(id=uuid.uuid4())
    assert follow is None
    session.close()


def test_get_follow_for_follower_and_following(
    before_create_normal_user, before_create_follow_request
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    follow = FollowService(session=session).get_follow_for_follower_and_following(
        follower_id=user1.id, following_id=user2.id
    )
    assert db_follow == follow
    session.close()


def test_get_follow_for_follower_and_following_for_no_user():
    session = create_session()
    follow = FollowService(session=session).get_follow_for_follower_and_following(
        follower_id=uuid.uuid4(), following_id=uuid.uuid4()
    )
    assert follow is None
    session.close()


def test_create(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    follow = FollowService(session=session).create(
        follow={
            "follower_id": user1.id,
            "following_id": user2.id,
            "status": StatusType.PENDING,
        }
    )
    assert follow.follower_id == user1.id
    assert follow.following_id == user2.id
    assert follow.status == StatusType.PENDING.value
    session.close()


def test_create_with_invalid_user_data(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    with pytest.raises(IntegrityError):
        FollowService(session=session).create(
            follow={
                "follower_id": user1.id,
                "following_id": uuid.uuid4(),
                "status": StatusType.PENDING,
            }
        )
    session.close()


def test_create_without_status(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    follow = FollowService(session=session).create(
        follow={"follower_id": user1.id, "following_id": user2.id}
    )
    assert follow.follower_id == user1.id
    assert follow.following_id == user2.id
    assert follow.status == StatusType.PENDING.value
    session.close()


def test_create_without_following_id(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    with pytest.raises(ValidationError):
        FollowService(session=session).create(
            follow={"follower_id": user1.id, "status": StatusType.PENDING}
        )
    session.close()


def test_create_without_follower_id(before_create_normal_user):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    with pytest.raises(ValidationError):
        FollowService(session=session).create(
            follow={"following_id": user1.id, "status": StatusType.PENDING}
        )
    session.close()


def test_update(before_create_normal_user, before_create_approved_follow_requests):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    follow = FollowService(session=session).update(
        follow={
            "follower_id": user2.id,
            "following_id": user1.id,
            "status": StatusType.PENDING,
        },
        db_follow=db_follow,
    )
    assert follow.follower_id == user2.id
    assert follow.following_id == user1.id
    assert follow.status == StatusType.PENDING.value
    session.close()


def test_update_with_invalid_user_data(
    before_create_normal_user, before_create_approved_follow_requests
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    with pytest.raises(IntegrityError):
        FollowService(session=session).update(
            follow={
                "follower_id": user1.id,
                "following_id": uuid.uuid4(),
                "status": StatusType.PENDING,
            },
            db_follow=db_follow,
        )
    session.close()


def test_update_without_status(
    before_create_normal_user, before_create_approved_follow_requests
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    follow = FollowService(session=session).update(
        follow={"follower_id": user1.id, "following_id": user2.id}, db_follow=db_follow
    )
    assert follow.follower_id == user1.id
    assert follow.following_id == user2.id
    assert follow.status == StatusType.APPROVED.value
    session.close()


def test_update_without_following_id(
    before_create_normal_user, before_create_approved_follow_requests
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    user3 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    follow = FollowService(session=session).update(
        follow={"follower_id": user3.id, "status": StatusType.PENDING},
        db_follow=db_follow,
    )
    assert follow.follower_id == user3.id
    assert follow.following_id == user2.id
    assert follow.status == StatusType.PENDING.value
    session.close()


def test_update_without_follower_id(
    before_create_normal_user, before_create_approved_follow_requests
):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    user3 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_approved_follow_requests(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    follow = FollowService(session=session).update(
        follow={"following_id": user3.id, "status": StatusType.PENDING},
        db_follow=db_follow,
    )
    assert follow.follower_id == user1.id
    assert follow.following_id == user3.id
    assert follow.status == StatusType.PENDING.value
    session.close()


def test_delete(before_create_normal_user, before_create_follow_request):
    session = create_session()
    user1 = before_create_normal_user(session=session, user_dict=create_private_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    db_follow = before_create_follow_request(
        session=session, follower_id=user1.id, following_id=user2.id
    )
    FollowService(session=session).delete(db_follow=db_follow)
    follow = session.get(FollowersModel, db_follow.id)
    assert follow is None
