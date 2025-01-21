from typing import Annotated

from fastapi import Depends

from sqlmodel import Session, create_engine

from .settings import settings

sqlite_url = settings.DATABASE_URL

engine = create_engine(url=sqlite_url)

def get_session():
    """create session"""
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# @event.listens_for(BaseModel, "after_update")
# def update_modified_at(mapper, connection, target):
#     print("***", target)
#     target.modified_at = datetime.now(tz=get_default_timezone())