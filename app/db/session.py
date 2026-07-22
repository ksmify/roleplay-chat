from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


DATABASE_URL = getattr(
    settings,
    "database_url",
    "sqlite:///./anai.db",
)


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    }
    if DATABASE_URL.startswith("sqlite")
    else {},
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


from app.db import models  # noqa: E402


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(
        bind=engine
    )