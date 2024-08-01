from nonebot import get_driver

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

from . import config

_engine = create_engine(config.canrot_config.canrot_database)


class Base(DeclarativeBase):
    pass


def get_engine() -> Engine:
    return _engine


_session = sessionmaker(bind=get_engine())


def get_session() -> sessionmaker[Session]:
    return _session


def create_all_tables() -> None:
    Base.metadata.create_all(get_engine())


@get_driver().on_shutdown
async def _():
    _engine.dispose()


__all__ = ["Base", "get_engine", "get_session", "create_all_tables"]
