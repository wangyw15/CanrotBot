from nonebot import get_driver

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from . import config

_engine = create_engine(config.canrot_config.canrot_database)
_session = sessionmaker(bind=_engine)


def get_engine() -> Engine:
    return _engine


def get_session() -> sessionmaker[Session]:
    return _session


@get_driver().on_shutdown
async def _():
    _engine.dispose()


__all__ = ['get_engine']
