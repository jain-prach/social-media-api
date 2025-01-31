import uuid

import pytest
from sqlalchemy.exc import IntegrityError, DataError
from pydantic import ValidationError
# from psycopg2.errors import ForeignKeyViolation

from src.tests.test_client import setup_database
from src.domain.users.services import BaseUserService
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
    create_admin
)
from src.application.users.services import PasswordService
from src.domain.models import BaseUser
from lib.fastapi.custom_enums import Role


def test_get_base_user_by_email(before_create_base_user):
    session = create_session()
    base_user = before_create_base_user(session=session, user_dict=create_user())
    db_base_user = BaseUserService(session=session).get_base_user_by_email(
        email=base_user.email
    )
    assert db_base_user is not None
    assert db_base_user.id == base_user.id


def test_get_base_user_by_email_for_invalid_user():
    session = create_session()
    db_base_user = BaseUserService(session=session).get_base_user_by_email(
        email="invalid@gmail.com"
    )
    assert db_base_user is None


def test_get_base_user_by_id(before_create_base_user):
    session = create_session()
    base_user = before_create_base_user(session=session, user_dict=create_user())
    db_base_user = BaseUserService(session=session).get_base_user_by_id(id=base_user.id)
    assert db_base_user is not None
    assert db_base_user.id == base_user.id


def test_get_base_user_by_id_for_invalid_user():
    session = create_session()
    db_base_user = BaseUserService(session=session).get_base_user_by_id(id=uuid.uuid4())
    assert db_base_user is None


def test_get_base_user_by_user_id(before_create_normal_user):
    session = create_session()
    user = before_create_normal_user(session=session, user_dict=create_private_user())
    db_base_user = BaseUserService(session=session).get_base_user_by_user_id(
        user_id=user.id
    )
    assert db_base_user is not None
    assert db_base_user.id == user.base_user.id


def test_get_base_user_by_user_id_for_invalid_user_id():
    session = create_session()
    db_base_user = BaseUserService(session=session).get_base_user_by_user_id(
        user_id=uuid.uuid4()
    )
    assert db_base_user is None


def test_get_all_base_users(before_create_base_user):
    session = create_session()
    before_create_base_user(session=session, user_dict=create_user())
    before_create_base_user(session=session, user_dict=create_user())
    base_users = BaseUserService(session=session).get_all_base_users()
    assert len(base_users) == 2


def test_get_all_base_users_for_no_base_user_created():
    session = create_session()
    base_users = BaseUserService(session=session).get_all_base_users()
    assert base_users == []


def test_create_with_user_role():
    session = create_session()
    base_user = create_user()
    db_base_user = BaseUserService(session=session).create(
        base_user={
            "email": base_user.get("email"),
            "password": PasswordService().get_hashed_password(
                password=base_user.get("password")
            ),
            "role": base_user.get("role"),
        }
    )
    assert db_base_user is not None
    assert isinstance(db_base_user, BaseUser)

def test_create_with_admin_role():
    session = create_session()
    base_user = create_admin()
    db_base_user = BaseUserService(session=session).create(
        base_user={
            "email": base_user.get("email"),
            "password": PasswordService().get_hashed_password(
                password=base_user.get("password")
            ),
            "role": base_user.get("role"),
        }
    )
    assert db_base_user is not None
    assert isinstance(db_base_user, BaseUser)

def test_create_with_invalid_role():
    session = create_session()
    base_user = create_user()
    with pytest.raises(ValidationError):
        BaseUserService(session=session).create(
            base_user={
                "email": base_user.get("email"),
                "password": PasswordService().get_hashed_password(
                    password=base_user.get("password")
                ),
                "role": "invalid",
            }
        )

# def test_create_without_hashed_password():
#     # need to set a password validation check to ensure hash encryption
#     # right now handled based on length (which can break if password is 53 char long)
#     # wrong error raise too - Validation Error will return password should be 53 char long
#     session = create_session()
#     base_user = create_user()
#     with pytest.raises(ValidationError):
#         BaseUserService(session=session).create(
#             base_user={
#                 "email": base_user.get("email"),
#                 "password": base_user.get("password"),
#                 "role": base_user.get("role"),
#             }
#         )
#     session.close()

def test_create_with_existing_email_and_same_role(before_create_base_user):
    session = create_session()
    base_user = create_user()
    before_create_base_user(session=session, user_dict=base_user)
    with pytest.raises(IntegrityError):
        BaseUserService(session=session).create(
            base_user={
                "email": base_user.get("email"),
                "password": PasswordService().get_hashed_password(
                    password=base_user.get("password")
                ),
                "role": base_user.get("role"),
            }
        )

def test_create_with_existing_email_and_different_role(before_create_base_user):
    session = create_session()
    base_user = create_user()
    before_create_base_user(session=session, user_dict=base_user)
    with pytest.raises(IntegrityError):
        BaseUserService(session=session).create(
            base_user={
                "email": base_user.get("email"),
                "password": PasswordService().get_hashed_password(
                    password=base_user.get("password")
                ),
                "role": Role.ADMIN.value,
            }
        )

def test_create_without_email():
    session = create_session()
    base_user = create_user()
    with pytest.raises(ValidationError):
        BaseUserService(session=session).create(
            base_user={
                "password": PasswordService().get_hashed_password(
                    password=base_user.get("password")
                ),
                "role": base_user.get("role"),
            }
        )

def test_create_without_role():
    session = create_session()
    base_user = create_user()
    db_base_user = BaseUserService(session=session).create(
            base_user={
                "email": base_user.get("email"),
                "password": PasswordService().get_hashed_password(
                    password=base_user.get("password")
                ),
            }
        )
    assert db_base_user is not None
    assert db_base_user.role == Role.USER.value
    

def test_create_without_password():
    session = create_session()
    base_user = create_user()
    db_base_user = BaseUserService(session=session).create(
        base_user={
            "email": base_user.get("email"),
            "role": base_user.get("role"),
        }
    )
    assert db_base_user is not None
    assert isinstance(db_base_user, BaseUser)
    assert db_base_user.password is None

def test_update(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_admin())
    user_dict = create_user()
    update_dict = {
        "email": user_dict.get("email"),
        "password": PasswordService().get_hashed_password(password=user_dict.get("password")),
        "role": user_dict.get("role")
    }
    base_user = BaseUserService(session=session).update(base_user=update_dict, db_base_user=db_base_user)
    assert base_user is not None
    assert isinstance(base_user, BaseUser)
    assert base_user.email == update_dict.get("email")
    assert base_user.password == update_dict.get("password")
    assert base_user.role == update_dict.get("role")


def test_update_without_password(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_admin())
    user_dict = create_user()
    update_dict = {
        "email": user_dict.get("email"),
        "role": user_dict.get("role")
    }
    base_user = BaseUserService(session=session).update(base_user=update_dict, db_base_user=db_base_user)
    assert base_user is not None
    assert isinstance(base_user, BaseUser)
    assert base_user.email == update_dict.get("email")
    assert base_user.password == db_base_user.password
    assert base_user.role == update_dict.get("role")

def test_update_without_role(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_admin())
    user_dict = create_user()
    update_dict = {
        "email": user_dict.get("email"),
        "password": PasswordService().get_hashed_password(password=user_dict.get("password")),
    }
    base_user = BaseUserService(session=session).update(base_user=update_dict, db_base_user=db_base_user)
    assert base_user is not None
    assert isinstance(base_user, BaseUser)
    assert base_user.email == update_dict.get("email")
    assert base_user.password == update_dict.get("password")
    assert base_user.role == db_base_user.role

def test_update_without_email(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_admin())
    user_dict = create_user()
    update_dict = {
        "password": PasswordService().get_hashed_password(password=user_dict.get("password")),
        "role": user_dict.get("role")
    }
    base_user = BaseUserService(session=session).update(base_user=update_dict, db_base_user=db_base_user)
    assert base_user is not None
    assert isinstance(base_user, BaseUser)
    assert base_user.email == db_base_user.email
    assert base_user.password == update_dict.get("password")
    assert base_user.role == update_dict.get("role")

#ASK: sqlmodel_update doesn't validate values for sqlmodel table
# def test_update_without_hashed_password(before_create_base_user):
#     session = create_session()
#     db_base_user = before_create_base_user(session=session, user_dict=create_admin())
#     user_dict = create_user()
#     update_dict = {
#         "email": user_dict.get("email"),
#         "password":user_dict.get("password"),
#         "role": user_dict.get("role")
#     }
#     with pytest.raises(ValidationError):
#         BaseUserService(session=session).update(base_user=update_dict, db_base_user=db_base_user)


def test_update_with_invalid_role(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_admin())
    user_dict = create_user()
    update_dict = {
        "email": user_dict.get("email"),
        "password": PasswordService().get_hashed_password(password=user_dict.get("password")),
        "role": "invalid"
    }
    with pytest.raises(DataError):
        BaseUserService(session=session).update(base_user=update_dict, db_base_user=db_base_user)

def test_update_with_existing_user_email(before_create_base_user):
    session = create_session()
    db_base_user = before_create_base_user(session=session, user_dict=create_admin())
    db_base_user2 = before_create_base_user(session=session, user_dict=create_user())
    user_dict = create_user()
    update_dict = {
        "email": db_base_user2.email,
        "password": PasswordService().get_hashed_password(password=user_dict.get("password")),
        "role": user_dict.get("role")
    }
    with pytest.raises(IntegrityError):
        BaseUserService(session=session).update(base_user=update_dict, db_base_user=db_base_user)

def test_delete(before_create_base_user):
    session = create_session()
    base_user = before_create_base_user(session=session, user_dict=create_user())
    BaseUserService(session=session).delete(db_base_user=base_user)
    db_base_user = session.get(BaseUser, base_user.id)
    assert db_base_user is None