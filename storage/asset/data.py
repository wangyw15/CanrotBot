from datetime import datetime

from sqlalchemy import Column, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class RemoteAssetCache(Base):
    __tablename__ = "remote_asset_cache"

    id: Mapped[int] = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    key: Mapped[str] = Column(Text, nullable=False)
    fetch_time: Mapped[datetime] = Column(
        DateTime, nullable=False, default=datetime.now
    )
    expire_time: Mapped[datetime] = Column(DateTime, nullable=True)
    extra: Mapped[str] = Column(Text, nullable=True, default="")


Base.metadata.create_all(database.get_engine())
