from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

in_memory_engine = create_engine("sqlite:///:memory:")
SessionInMemory = sessionmaker(autocommit=False, autoflush=False, bind=in_memory_engine)

Base = declarative_base()
