from nonebot import get_driver

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from .model import Base
from .config import DatabaseConfig

config = DatabaseConfig()
engine = create_engine(config.connection_string)


def get_engine() -> Engine:
    return engine


session_maker = sessionmaker(bind=get_engine())


def get_session() -> sessionmaker[Session]:
    return session_maker


def create_all_tables() -> None:
    Base.metadata.create_all(get_engine())


@get_driver().on_shutdown
async def _():
    engine.dispose()


__all__ = ["Base", "get_engine", "get_session", "create_all_tables"]
