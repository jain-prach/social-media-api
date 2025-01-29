import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
# from psycopg2.errors import ForeignKeyViolation

from src.tests.test_client import setup_database
from src.domain.users.services import BaseUserService, OtpService
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


def test_get_base_user_by_email(before_create_base_user):
    session = create_session()
    user = before_create_base_user(session=session, user_dict=create_user())
    db_user = BaseUserService(session=session).get_base_user_by_email(email=user.email)
    assert db_user is not None
    assert db_user.id == user.id


def test_get_base_user_by_email_for_invalid_user():
    session = create_session()
    db_user = BaseUserService(session=session).get_base_user_by_email(email="invalid@gmail.com")
    assert db_user is None