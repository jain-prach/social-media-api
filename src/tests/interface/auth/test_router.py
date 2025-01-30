from datetime import datetime, timedelta
import jwt

from sqlmodel import select

from src.domain.models import BaseUser, Otp
from src.tests.test_client import client, setup_database
from src.tests.test_data import (
    admin_registration_wrong_email,
    created_user_login_invalid_password,
    invalid_login,
    create_user,
    create_admin,
    created_user,
    weak_password,
    invalid_role,
    no_password,
    no_email,
    no_role,
)
from src.tests.test_utils import create_session
from lib.fastapi.custom_enums import Role
from src.application.users.services import JWTService
from lib.fastapi.utils import generate_otp, get_default_timezone
from src.setup.config.settings import settings
from src.tests.test_fixtures import (
    before_create_base_user,
    before_create_otp,
    before_create_otp_token,
)


def test_registration_admin():
    """create admin with correct data"""
    response = client.post(
        url="/register/",
        json=create_admin(),
    )
    data = response.json()["data"]
    assert response.status_code == 201
    assert data["role"] == Role.ADMIN.value


def test_registration_with_wrong_email():
    """register with wrong email"""
    response = client.post(url="/register/", json=admin_registration_wrong_email())
    assert response.status_code == 422


def test_registration_user():
    """create user with correct data"""
    response = client.post(
        url="/register/",
        json=create_user(),
    )
    data = response.json()["data"]
    assert response.status_code == 201
    assert data["role"] == Role.USER.value


def test_registration_without_password():
    response = client.post(
        url="/register/",
        json=no_password,
    )
    assert response.status_code == 422


def test_registration_without_role():
    response = client.post(
        url="/register/",
        json=no_role,
    )
    assert response.status_code == 422


def test_registration_without_email():
    response = client.post(
        url="/register/",
        json=no_email,
    )
    assert response.status_code == 422


def test_registration_with_weak_password():
    response = client.post(
        url="/register/",
        json=weak_password,
    )
    assert response.status_code == 422


def test_registration_with_wrong_role():
    response = client.post(
        url="/register/",
        json=invalid_role,
    )
    assert response.status_code == 422


def test_login(before_create_base_user):
    """test login response"""
    session = create_session()
    user = before_create_base_user(session=session, user_dict=create_user())
    response = client.post(url="/login/", json=created_user(email=user.email))
    data = response.json()["data"]
    assert response.status_code == 200
    assert "access_token" in data.keys()
    payload = JWTService().decode(token=data["access_token"])
    assert payload.get("id") == str(user.id)
    session.close()


def test_login_invalid_data():
    """test login with invalid data"""
    response = client.post(url="/login/", json=invalid_login)
    assert response.status_code == 401


def test_login_invalid_password(before_create_base_user):
    session = create_session()
    user = before_create_base_user(session=session, user_dict=create_user())
    response = client.post(
        url="/login", json=created_user_login_invalid_password(email=user.email)
    )
    session.close()
    assert response.status_code == 401


def test_forgot_password(before_create_base_user):
    session = create_session()
    user = before_create_base_user(session=session, user_dict=create_user())
    email = user.email
    response = client.post(url="/forgot-password/", json={"email": email})
    db_user = session.scalars(select(BaseUser).where(BaseUser.email == email)).first()
    otp = db_user.otp
    session.close()
    assert response.status_code == 200
    assert otp is not None


def test_forgot_password_invalid_email():
    response = client.post(url="/forgot-password/", json={"email": "invalid"})
    assert response.status_code == 422


def test_forgot_password_for_user_not_created():
    email = invalid_login["email"]
    response = client.post(url="/forgot-password/", json={"email": email})
    session = create_session()
    otp_user_emails = [otp.base_user.email for otp in session.exec(select(Otp)).all()]
    session.close()
    assert response.status_code == 200
    assert email not in otp_user_emails


def test_verify_otp(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    email = otp.base_user.email
    otp = otp.otp
    response = client.post(url="/verify-otp/", json={"otp": otp, "email": email})
    data = response.json()["data"]
    session.close()
    assert response.status_code == 200
    assert "otp_token" in data.keys()


def test_verify_otp_with_wrong_otp(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    email = otp.base_user.email
    wrong_otp = generate_otp()
    response = client.post(url="/verify-otp/", json={"otp": wrong_otp, "email": email})
    data = response.json()["data"]
    session.close()
    assert response.status_code == 401
    assert "otp_token" not in data.keys()


def test_reset_password(before_create_otp_token):
    session = create_session()
    otp_token = before_create_otp_token(session)
    response = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": "Practice@123New"},
    )
    session.close()
    assert response.status_code == 200

def test_reset_password_with_weak_password(before_create_otp_token):
    session = create_session()
    otp_token = before_create_otp_token(session)
    response = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": "weak"},
    )
    session.close()
    assert response.status_code == 422


def test_reset_password_invalid_token(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    otp_token = jwt.encode(
        payload={
            "id": str(otp.base_user.id),
            "otp": otp.otp,
            "exp": datetime.now(tz=get_default_timezone()) + timedelta(**settings.OTP_EXPIRE_TIME),
        },
        key="secret",
        algorithm="HS256",
    )
    response = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": "Practice@123New"},
    )
    session.close()
    assert response.status_code == 401


def test_reset_password_invalid_token_payload(before_create_otp):
    session = create_session()
    otp = before_create_otp(session)
    otp_token = JWTService().create_access_token(
        data={"otp": otp.otp},
        expire=datetime.now(tz=get_default_timezone()) + timedelta(**settings.OTP_EXPIRE_TIME),
    )
    response = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": "Practice@123New"},
    )
    session.close()
    assert response.status_code == 400


def test_forgot_password_flow(before_create_base_user):
    session = create_session()
    user = before_create_base_user(session=session, user_dict=create_user())
    email = user.email
    response = client.post(url="/forgot-password/", json={"email": email})
    assert response.status_code == 200
    # can't get it from response as user email is sent
    otp = user.otp.otp
    response2 = client.post(url="/verify-otp/", json={"otp": otp, "email": email})
    assert response2.status_code == 200
    otp_token = response2.json()["data"]["otp_token"]
    new_password = "Practice@123New"
    response3 = client.post(
        url="/reset-password/",
        json={"otp_token": otp_token, "new_password": new_password},
    )
    assert response3.status_code == 200
    # login with new password
    response4 = client.post(
        url="/login/", json={"email": email, "password": new_password}
    )
    assert response4.status_code == 200
    assert "access_token" in (response4.json()["data"]).keys()
