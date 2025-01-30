from faker import Faker

from lib.fastapi.custom_enums import Role, ProfileType
from src.domain.models import User

fake = Faker()


def get_username():
    return fake.user_name()


def get_email():
    return fake.email()


def create_admin():
    return {
        "email": fake.email(),
        "role": Role.ADMIN,
        "password": "Practice@123",
    }


def create_user():
    return {
        "email": fake.email(),
        "role": Role.USER,
        "password": "Practice@123",
    }


def created_user(email: str):
    return {"email": email, "password": "Practice@123"}


def created_user_login_invalid_password(email):
    return {
        "email": email,
        "password": "invalid",
    }


weak_password = {"email": fake.email(), "password": "weak", "role": Role.ADMIN}
invalid_role = {"email": fake.email(), "password": "weak", "role": "invalid"}
no_password = {"email": fake.email(), "role": Role.ADMIN}
no_role = {"email": fake.email(), "password": "Practice@123"}
no_email = {"password": "Practice@123", "role": Role.ADMIN}

invalid_login = {"email": fake.email(), "password": "invalid"}


def admin_registration_wrong_email():
    return {
        "email": "invalid",
        "role": Role.ADMIN,
        "password": "Practice@123",
    }


def user_registration_wrong_email():
    return {
        "email": "invalid",
        "role": Role.USER,
        "password": "Practice@123",
    }


def create_public_user():
    return {
        "username": fake.user_name(),
        "bio": fake.text(max_nb_chars=20),
        "profile_type": ProfileType.PUBLIC,
    }


def create_private_user():
    return {
        "username": fake.user_name(),
        "bio": fake.text(max_nb_chars=20),
        "profile_type": ProfileType.PRIVATE,
    }


def get_user_dict_from_user(user: User):
    return {
        "username": user.username,
        "bio": user.bio,
        "profile_type": user.profile_type,
    }
