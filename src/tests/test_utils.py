from sqlmodel import Session

from src.tests.test_client import override_get_session

def create_session() -> Session:
    session = list(override_get_session())[0]
    return session

def create_value_using_session(session:Session, value):
    session.add(value)
    session.commit()
    session.refresh(value)
    return value
