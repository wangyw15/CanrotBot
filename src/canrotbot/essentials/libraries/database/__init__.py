from nonebot import get_driver, get_plugin_config
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import DatabaseConfig
from .model import Base

config = get_plugin_config(DatabaseConfig)
engine = create_engine(config.connection_string, pool_pre_ping=True, pool_recycle=600)


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
