import pytest

from fastapi.testclient import TestClient

from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.orm.session import close_all_sessions


from src.infrastructure.file_upload.services import Boto3Service
from src.setup.app_factory import app
from src.setup.config.settings import settings
from src.setup.config.database import get_session
from lib.fastapi.custom_enums import Environment

settings.ENVIRONMENT = Environment.TESTING.value

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

test_engine = create_engine(url=TEST_DATABASE_URL)


def override_get_session():
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    SQLModel.metadata.create_all(test_engine)
    db = list(override_get_session())[0]
    # print("************",db.exec(select(BaseUser)).all())
    db.rollback()
    yield db
    # db.close_all()
    close_all_sessions()
    Boto3Service().delete_bucket(bucket_name=settings.TEST_AWS_BUCKET_NAME)
    SQLModel.metadata.drop_all(test_engine)


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)
