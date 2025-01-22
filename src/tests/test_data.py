from faker import Faker

from lib.fastapi.custom_enums import Role

fake = Faker()

create_admin = {
    "email": fake.email(),
    "role": Role.ADMIN,
    "password": "Practice@123",
}

create_user = {
    "email": fake.email(),
    "role": Role.USER,
    "password": "Practice@123",
}

created_admin_login = {
    "email": create_admin["email"],
    "password": create_admin["password"],
}
created_user_login = {
    "email": create_user["email"],
    "password": create_user["password"],
}
created_user_login_invalid_password = {
    "email": create_user["email"],
    "password": "invalid",
}
invalid_login = {"email": fake.email(), "password": "invalid"}

admin_registration_correct_data = {
    "email": fake.email(),
    "role": Role.ADMIN,
    "password": "Practice@123",
}

admin_registration_wrong_email = {
    "email": "invalid",
    "role": Role.ADMIN,
    "password": "Practice@123",
}

user_registration_correct_data = {
    "email": fake.email(),
    "role": Role.USER,
    "password": "Practice@123",
}

user_registration_wrong_email = {
    "email": "invalid",
    "role": Role.USER,
    "password": "Practice@123",
}
