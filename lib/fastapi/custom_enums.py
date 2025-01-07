from enum import Enum


class Role(str, Enum):
    """enum for role: user and admin"""
    USER = "user"
    ADMIN = "admin"


class ProfileType(str, Enum):
    """enum for profile type: public and private"""
    PUBLIC = "public"
    PRIVATE = "private"
