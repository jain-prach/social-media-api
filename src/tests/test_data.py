from faker import Faker

from lib.fastapi.custom_enums import Role

fake = Faker()

create_admin = {
    "username": fake.name().split(" ")[0],
    "email": fake.email(),
    "role": Role.ADMIN,
    "password": "Practice@123",
}

create_user = {
    "username": fake.name().split(" ")[0],
    "email": fake.email(),
    "role": Role.USER,
    "password": "Practice@123",
}

created_admin_login = {"email": create_admin["email"], "password": create_admin["password"]}
created_user_login = {"email": create_user["email"], "password": create_user["password"]}

admin_registration = {
    "username": fake.name().split(" ")[0],
    "email": fake.email(),
    "role": Role.ADMIN,
    "password": "Practice@123",
}

user_registration = {
    "username": fake.name().split(" ")[0],
    "email": fake.email(),
    "role": Role.USER,
    "password": "Practice@123",
}