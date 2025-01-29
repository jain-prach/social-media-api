import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
# from psycopg2.errors import ForeignKeyViolation

from src.tests.test_client import setup_database
from src.domain.users.users.services import UserService
from src.tests.test_utils import create_session
from src.tests.test_fixtures import (
    before_create_base_user,
    before_create_normal_user,
)
from src.tests.test_data import (
    create_private_user,
    create_public_user,
    get_username,
    create_user,
)
from lib.fastapi.custom_enums import ProfileType
from src.domain.models import User


def test_get_user_by_username(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    db_user = UserService(session=session).get_user_by_username(username=user.username)
    assert db_user is not None
    assert db_user.id == user.id


def test_get_user_by_username_for_invalid_user():
    session = create_session()
    db_user = UserService(session=session).get_user_by_username(username=get_username())
    assert db_user is None


def test_get_user_by_id(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    db_user = UserService(session=session).get_user_by_id(id=user.id)
    assert db_user is not None
    assert db_user.id == user.id


def test_get_user_by_id_for_invalid_user():
    session = create_session()
    db_user = UserService(session=session).get_user_by_id(id=uuid.uuid4())
    assert db_user is None


def test_get_user_by_base_user_id(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    db_user = UserService(session=session).get_user_by_base_user_id(
        base_user_id=user.base_user_id
    )
    assert db_user is not None
    assert db_user.id == user.id


def test_get_user_by_base_user_id_for_invalid_user():
    session = create_session()
    db_user = UserService(session=session).get_user_by_base_user_id(
        base_user_id=uuid.uuid4()
    )
    assert db_user is None


def test_get_all_users(before_create_normal_user):
    session = create_session()
    before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_normal_user(session=session, user_dict=create_public_user())
    users = UserService(session=session).get_all_users()
    assert len(users) == 2


def test_get_all_users_when_no_user_is_created():
    session = create_session()
    users = UserService(session=session).get_all_users()
    assert len(users) == 0


def test_get_all_public_users(before_create_normal_user):
    session = create_session()
    before_create_normal_user(session=session, user_dict=create_private_user())
    before_create_normal_user(session=session, user_dict=create_public_user())
    users = UserService(session=session).get_all_public_users()
    assert len(users) == 1


def test_get_all_public_users_when_no_public_user_is_created(before_create_normal_user):
    session = create_session()
    before_create_normal_user(session=session, user_dict=create_private_user())
    users = UserService(session=session).get_all_public_users()
    assert len(users) == 0


def test_create(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_user())
    db_user = UserService(session=session).create(
        user={
            "username": get_username(),
            "bio": "randomtext",
            "profile_type": ProfileType.PRIVATE.value,
            "profile": "object_key",
            "base_user_id": db_base_user.id,
        }
    )
    assert db_user is not None
    assert isinstance(db_user, User)


def test_create_with_invalid_base_user_id():
    session = create_session()
    with pytest.raises(IntegrityError):
        UserService(session=session).create(
            user={
                "username": get_username(),
                "bio": "randomtext",
                "profile_type": ProfileType.PRIVATE.value,
                "profile": "object_key",
                "base_user_id": uuid.uuid4(),
            }
        )
    session.close()


def test_create_with_already_used_base_user_id(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    with pytest.raises(IntegrityError):
        UserService(session=session).create(
            user={
                "username": get_username(),
                "bio": "randomtext",
                "profile_type": ProfileType.PRIVATE.value,
                "profile": "object_key",
                "base_user_id": user.base_user_id,
            }
        )
    session.close()


def test_create_without_profile_type(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_user())
    db_user = UserService(session=session).create(
        user={
            "username": get_username(),
            "bio": "randomtext",
            "profile": "object_key",
            "base_user_id": db_base_user.id,
        }
    )
    assert db_user is not None
    assert isinstance(db_user, User)
    assert db_user.profile_type == ProfileType.PUBLIC.value


def test_create_without_profile(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_user())
    db_user = UserService(session=session).create(
        user={
            "username": get_username(),
            "bio": "randomtext",
            "profile_type": ProfileType.PRIVATE.value,
            "base_user_id": db_base_user.id,
        }
    )
    assert db_user is not None
    assert isinstance(db_user, User)
    assert db_user.profile is None


def test_create_without_base_user_id():
    session = create_session()
    with pytest.raises(ValidationError):
        UserService(session=session).create(
            user={
                "username": get_username(),
                "bio": "randomtext",
                "profile_type": ProfileType.PRIVATE.value,
                "profile": "object_key",
            }
        )


def test_create_without_bio(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_user())
    db_user = UserService(session=session).create(
        user={
            "username": get_username(),
            "profile_type": ProfileType.PRIVATE.value,
            "profile": "object_key",
            "base_user_id": db_base_user.id,
        }
    )
    assert db_user is not None
    assert isinstance(db_user, User)
    assert db_user.bio is None


def test_create_without_username(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_user())
    with pytest.raises(ValidationError):
        UserService(session=session).create(
            user={
                "bio": "randomtext",
                "profile_type": ProfileType.PRIVATE.value,
                "profile": "object_key",
                "base_user_id": db_base_user.id,
            }
        )


def test_update(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    user_dict = {
        "username": get_username(),
        "bio": "randomtext_update",
        "profile_type": ProfileType.PRIVATE.value,
        "profile": "object_key_update",
        "base_user_id": db_user.base_user_id,
    }
    user = UserService(session=session).update(user=user_dict, db_user=db_user)
    assert user is not None
    assert isinstance(user, User)
    assert user.profile_type == user_dict.get("profile_type")
    assert user.username == user_dict.get("username")
    assert user.bio == user_dict.get("bio")
    assert user.profile == user_dict.get("profile")


def test_update_with_invalid_base_user_id(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    with pytest.raises(IntegrityError):
        UserService(session=session).update(
            user={
                "username": get_username(),
                "bio": "randomtext",
                "profile_type": ProfileType.PRIVATE.value,
                "profile": "object_key",
                "base_user_id": uuid.uuid4(),
            },
            db_user=db_user,
        )


def test_update_with_existing_base_user_id(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    user2 = before_create_normal_user(session=session, user_dict=create_private_user())
    with pytest.raises(IntegrityError):
        UserService(session=session).update(
            user={
                "username": get_username(),
                "bio": "randomtext",
                "profile_type": ProfileType.PRIVATE.value,
                "profile": "object_key",
                "base_user_id": user2.base_user_id,
            },
            db_user=db_user,
        )

def test_update_without_username(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    user_dict = {
        "bio": "randomtext_update",
        "profile_type": ProfileType.PRIVATE.value,
        "profile": "object_key_update",
        "base_user_id": db_user.base_user_id,
    }
    user = UserService(session=session).update(user=user_dict, db_user=db_user)
    assert user is not None
    assert isinstance(user, User)
    assert user.profile_type == user_dict.get("profile_type")
    assert user.bio == user_dict.get("bio")
    assert user.profile == user_dict.get("profile")
    assert user.username == db_user.username

def test_update_without_bio(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    user_dict = {
        "username": get_username(),
        "profile_type": ProfileType.PRIVATE.value,
        "profile": "object_key_update",
        "base_user_id": db_user.base_user_id,
    }
    user = UserService(session=session).update(user=user_dict, db_user=db_user)
    assert user is not None
    assert isinstance(user, User)
    assert user.profile_type == user_dict.get("profile_type")
    assert user.username == user_dict.get("username")
    assert user.profile == user_dict.get("profile")
    assert user.bio == db_user.bio

def test_update_without_profile_type(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    user_dict = {
        "username": get_username(),
        "bio": "randomtext_update",
        "profile": "object_key_update",
        "base_user_id": db_user.base_user_id,
    }
    user = UserService(session=session).update(user=user_dict, db_user=db_user)
    assert user is not None
    assert isinstance(user, User)
    assert user.username == user_dict.get("username")
    assert user.bio == user_dict.get("bio")
    assert user.profile == user_dict.get("profile")
    assert user.profile_type == db_user.profile_type

def test_update_without_profile(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    user_dict = {
        "username": get_username(),
        "bio": "randomtext_update",
        "profile_type": ProfileType.PRIVATE.value,
        "base_user_id": db_user.base_user_id,
    }
    user = UserService(session=session).update(user=user_dict, db_user=db_user)
    assert user is not None
    assert isinstance(user, User)
    assert user.profile_type == user_dict.get("profile_type")
    assert user.username == user_dict.get("username")
    assert user.bio == user_dict.get("bio")
    assert user.profile == db_user.profile

def test_update_without_base_user_id(before_create_normal_user):
    session = create_session()
    db_user = before_create_normal_user(session=session, user_dict=create_public_user())
    user_dict = {
        "username": get_username(),
        "bio": "randomtext_update",
        "profile_type": ProfileType.PRIVATE.value,
        "profile": "object_key_update",
    }
    user = UserService(session=session).update(user=user_dict, db_user=db_user)
    assert user is not None
    assert isinstance(user, User)
    assert user.profile_type == user_dict.get("profile_type")
    assert user.username == user_dict.get("username")
    assert user.bio == user_dict.get("bio")
    assert user.profile == user_dict.get("profile")
    assert user.base_user_id == db_user.base_user_id


def test_delete(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    UserService(session=session).delete(user=user)
    db_user = session.get(User, user.id)
    assert db_user is None
