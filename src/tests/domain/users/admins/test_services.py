import uuid

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.tests.test_client import setup_database
from src.tests.test_data import create_admin
from src.tests.test_fixtures import before_create_base_user, before_create_admin
from src.tests.test_utils import create_session
from src.domain.users.admins.services import AdminService
from src.domain.models import Admin

def test_get_admin_by_base_user_id(before_create_admin):
    session = create_session()
    admin = before_create_admin(session=session)
    db_admin = AdminService(session=session).get_admin_by_base_user_id(base_user_id=admin.base_user_id)
    assert db_admin is not None
    assert db_admin.base_user_id == admin.base_user_id
    assert db_admin.id == admin.id

def test_get_admin_by_invalid_base_user_id():
    session = create_session()
    db_admin = AdminService(session=session).get_admin_by_base_user_id(base_user_id=uuid.uuid4())
    assert db_admin is None

def test_get_admin_by_base_user_id_for_no_admin_created(before_create_base_user):
    session = create_session()
    base_user = before_create_base_user(session=session, user_dict=create_admin())
    db_admin = AdminService(session=session).get_admin_by_base_user_id(base_user_id=base_user.id)
    assert db_admin is None

def test_create(before_create_base_user):
    session = create_session()
    base_user = before_create_base_user(session=session, user_dict=create_admin())
    db_admin = AdminService(session=session).create(admin={
        "base_user_id": base_user.id
    })
    assert db_admin is not None
    assert db_admin.base_user == base_user

def test_create_with_invalid_base_user_id():
    session = create_session()
    with pytest.raises(IntegrityError):
        AdminService(session=session).create(admin={"base_user_id": uuid.uuid4()})

def test_create_without_base_user_id():
    session = create_session()
    with pytest.raises(ValidationError):
        AdminService(session=session).create(admin={"base_user_id": None})

def test_delete(before_create_admin):
    session = create_session()
    db_admin = before_create_admin(session=session)
    AdminService(session=session).delete(db_admin=db_admin)
    admin = session.get(Admin, db_admin.id)
    assert admin is None