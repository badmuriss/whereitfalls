import logging
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    if database_url.startswith("postgresql"):
        return {"connect_timeout": 2}
    return {}


@lru_cache
def get_engine(database_url: str):
    return create_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
        connect_args=_connect_args(database_url),
    )


def init_database(settings: Settings | None = None) -> bool:
    settings = settings or get_settings()
    try:
        import app.models.domain  # noqa: F401

        engine = get_engine(settings.database_url)
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as exc:
        logger.warning("database_init_failed", extra={"error": str(exc)})
        return False
    return True


def get_session(settings: Settings | None = None) -> Generator[Session]:
    settings = settings or get_settings()
    engine = get_engine(settings.database_url)
    with Session(engine) as session:
        yield session
