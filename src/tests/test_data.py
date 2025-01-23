from faker import Faker

from lib.fastapi.custom_enums import Role, ProfileType

fake = Faker()

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

def created_user(email:str):
    return {
        "email": email,
        "password": "Practice@123"
    }

def created_user_login_invalid_password(email):
    return {
        "email": email,
        "password": "invalid",
    }

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