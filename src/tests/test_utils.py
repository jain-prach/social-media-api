from sqlmodel import Session, select

from src.tests.test_client import override_get_session
from src.domain.models import User
from src.application.users.services import JWTService

def create_session() -> Session:
    session = list(override_get_session())[0]
    return session

def create_value_using_session(session:Session, value):
    session.add(value)
    session.commit()
    session.refresh(value)
    return value

def get_auth_header(token:str) -> dict:
    return {'Authorization': f"Bearer {token}"}

def get_user_by_token(session:Session, token:str) -> User:
    payload = JWTService().decode(token=token)
    user = session.scalars(select(User).where(User.base_user_id == payload.get("id"))).first()
    return user

# def create_user_when_not_created(session:Session, user_dict:dict):
#     user = session.scalars(
#             select(User).where(User.username == user_dict["username"])
#         ).first()
#     if not user:
#         user = before_create_normal_user(session=session, user_dict=user_dict)