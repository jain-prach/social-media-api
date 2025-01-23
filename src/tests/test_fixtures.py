from datetime import datetime, timedelta

import pytest
from sqlmodel import Session

from src.domain.models import BaseUser, Otp, User
from .test_data import create_user, create_admin, create_public_user, create_private_user
from src.application.users.services import PasswordService, JWTService
from src.application.users.users.services import UserAppService
from .test_utils import create_value_using_session
from src.setup.config.settings import settings


@pytest.fixture(scope="function")
def before_create_base_user() -> BaseUser:
    def create_base_user(session: Session, user_dict:dict):
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
def before_admin_login_cred(before_create_base_user_admin) -> str:
    def admin_login_cred(session: Session): 
        db_base_user = before_create_base_user_admin(session=session, user_dict=create_admin())
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
def before_create_public_user(before_create_base_user) -> str:
    def create_public_user_fixture(session: Session):
        db_base_user=before_create_base_user(session=session, user_dict=create_user())
        user_dict = create_public_user()
        print(user_dict)
        with open("C:/Users/Prachi Citrusbug/Downloads/logo.jpg", 'r') as f:
            object_key = UserAppService.handle_profile_upload(profile=f, user={**user_dict, "base_user_id":db_base_user.id})
            db_user = User.model_validate({**user_dict, "profile":object_key, "base_user_id":db_base_user.id})
            create_value_using_session(session=session, value=db_user)
        return db_user
    return create_public_user_fixture


@pytest.fixture(scope="function")
def before_create_private_user(before_create_base_user) -> str:
    def create_private_user_fixture(session: Session):
        db_base_user=before_create_base_user(session=session, user_dict=create_user())
        user_dict = create_private_user()
        with open("C:/Users/Prachi Citrusbug/Downloads/logo.jpg") as f:
            object_key = UserAppService.handle_profile_upload(profile=f, user={**user_dict, "base_user_id":db_base_user.id})
            db_user = User.model_validate({**user_dict, "profile":object_key, "base_user_id":db_base_user.id})
            create_value_using_session(session=session, value=db_user)
        return db_user
    return create_private_user_fixture