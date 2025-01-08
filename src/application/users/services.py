from passlib.context import CryptContext

from sqlmodel import Session

from src.domain.models import BaseUser
from src.interface.users.schemas import CreateBaseUser


class PasswordService:
    """services for password handling"""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(PasswordService, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_hashed_password(self, password: str) -> str:
        return self.PASSWORD_CONTEXT.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.PASSWORD_CONTEXT.verify(password, hashed_password)


class UserService:
    """services for base user model"""

    def __init__(self, session: Session):
        self.db_session = session

    def create_user(self, user: CreateBaseUser) -> BaseUser:
        user.password = PasswordService().get_hashed_password(user.password)
        # print(user)
        db_user = BaseUser.model_validate(user)
        self.db_session.add(db_user)
        self.db_session.commit()
        self.db_session.refresh(db_user)
        return db_user
