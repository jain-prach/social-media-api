from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ProfileType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
