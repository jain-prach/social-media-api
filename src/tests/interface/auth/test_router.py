from datetime import datetime, timedelta
import jwt
import pytest

from sqlmodel import select, Session

from src.domain.models import BaseUser, Otp
from src.tests.test_client import client, setup_database
from src.tests.test_data import (
    admin_registration_correct_data,
    user_registration_correct_data,
    admin_registration_wrong_email,
    create_user,
    created_user_login,
    created_user_login_invalid_password,
    invalid_login,
)
from src.tests.test_utils import create_value_using_session, create_session
from lib.fastapi.custom_enums import Role
from src.application.users.services import PasswordService, JWTService
from lib.fastapi.utils import generate_otp
from src.setup.config.settings import settings


@pytest.fixture(scope="function")
def before_create_base_user() -> BaseUser:
    def create_base_user(session: Session):
        create_user["password"] = PasswordService().get_hashed_password(
            create_user["password"]
        )
        db_user = BaseUser.model_validate(create_user)
        create_value_using_session(session=session, value=db_user)
        return db_user

    return create_base_user


@pytest.fixture(scope="function")
def before_create_otp(before_create_base_user):
    def create_otp(session: Session):
        user = before_create_base_user(session=session)
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


def test_admin_registration():
    """create admin with correct data"""
    response = client.post(
        url="/register/",
        json=admin_registration_correct_data,
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["role"] == Role.ADMIN.value


def test_registration_with_wrong_email():
    """register with wrong email"""
    response = client.post(url="/register/", json=admin_registration_wrong_email)
    assert response.status_code == 422


def test_user_registration():
    """create user with correct data"""
    response = client.post(
        url="/register/",
        json=user_registration_correct_data,
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["role"] == Role.USER.value


def test_login(before_create_base_user):
    """test login response"""
    session = create_session()
    before_create_base_user(session)
    response = client.post(url="/login/", json=created_user_login)
    assert response.status_code == 200
    data = response.json()["data"]
    assert "access_token" in data.keys()
    session.close()


def test_login_invalid_data():
    """test login with invalid data"""
    response = client.post(url="/login/", json=invalid_login)
    assert response.status_code == 401


def test_login_invalid_password():
    response = client.post(url="/login", json=created_user_login_invalid_password)
    assert response.status_code == 401


def test_forgot_password(before_create_base_user):
    session = create_session()
    before_create_base_user(session)
    email = created_user_login["email"]
    response = client.post(url="/forgot-password/", json={"email": email})
    assert response.status_code == 200
    db_user = session.scalars(select(BaseUser).where(BaseUser.email == email)).first()
    assert db_user.otp is not None
    session.close()


def test_forgot_password_for_user_not_created():
    email = invalid_login["email"]
    response = client.post(url="/forgot-password/", json={"email": email})
    assert response.status_code == 200
    session = create_session()
    otp_user_emails = [otp.base_user.email for otp in session.exec(select(Otp)).all()]
    assert email not in otp_user_emails
    session.close()


def test_verify_otp(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    email = otp.base_user.email
    otp = otp.otp
    response = client.post(url="/verify-otp/", json={"otp": otp, "email": email})
    assert response.status_code == 200
    data = response.json()["data"]
    assert "otp_token" in data.keys()
    session.close()


def test_verify_otp_with_wrong_otp(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    email = otp.base_user.email
    wrong_otp = generate_otp()
    response = client.post(url="/verify-otp/", json={"otp": wrong_otp, "email": email})
    assert response.status_code == 401
    data = response.json()["data"]
    assert "otp_token" not in data.keys()
    session.close()


def test_reset_password(before_create_otp_token):
    session = create_session()
    otp_token = before_create_otp_token(session)
    response = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": "Practice@123New"},
    )
    assert response.status_code == 200
    session.close()


def test_reset_password_invalid_token(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    otp_token = jwt.encode(
        payload={
            "id": str(otp.base_user.id),
            "otp": otp.otp,
            "exp": datetime.now() + timedelta(**settings.OTP_EXPIRE_TIME),
        },
        key="secret",
        algorithm="HS256",
    )
    response = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": "Practice@123New"},
    )
    assert response.status_code == 401
    session.close()

def test_reset_password_invalid_token_payload(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    otp_token = JWTService().create_access_token(
            data={"otp": otp.otp},
            expire=datetime.now() + timedelta(**settings.OTP_EXPIRE_TIME),
        )
    response = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": "Practice@123New"},
    )
    assert response.status_code == 401
    session.close()