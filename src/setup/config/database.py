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