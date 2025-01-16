import pytest

from fastapi.testclient import TestClient

from sqlmodel import Session, create_engine, SQLModel

from src.setup.app_factory import app
from src.setup.config.settings import settings
from src.setup.config.database import get_session
from tests.test_dicts import create_admin, create_user

TEST_DATABASE_URL = settings.TEST_DATABASE_URL 

test_engine = create_engine(url=TEST_DATABASE_URL)

def override_get_session():
    with Session(test_engine) as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)

app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)