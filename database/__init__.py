import sqlalchemy as sa
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

in_memory_engine = create_engine("sqlite:///:memory:")
SessionInMemory = sessionmaker(autocommit=False, autoflush=False, bind=in_memory_engine)

Base = declarative_base()


class IdentifiedCreatedUpdated:
    id = sa.Column(sa.Integer, primary_key=True)
    created_at = sa.Column(sa.DateTime, server_default=func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, onupdate=func.current_timestamp(), nullable=True)
