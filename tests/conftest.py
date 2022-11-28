import pytest
from sqlalchemy.orm import clear_mappers

from database import Base, SessionLocal, SessionInMemory, in_memory_engine
from database.models import start_mappers
from database.repository import SqlAlchemyRepository


@pytest.fixture
def session_in_memory_mapped():
    session = SessionInMemory()
    Base.metadata.create_all(in_memory_engine)
    try:
        start_mappers(in_memory_engine)
        yield session
    finally:
        clear_mappers()
        session.close()


@pytest.fixture
def session_local():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def session_in_memory():
    Base.metadata.create_all(in_memory_engine)
    session = SessionInMemory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(in_memory_engine)


@pytest.fixture
def repo_in_memory(session_in_memory):
    repo = SqlAlchemyRepository(session_in_memory)
    try:
        yield repo
    finally:
        session_in_memory.close()
