from datetime import datetime

from sqlalchemy import Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class RemoteAssetCache(database.Base):
    __tablename__ = "remote_asset_cache"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    key: Mapped[str] = mapped_column(Text, nullable=False)
    fetch_time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    expire_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    extra: Mapped[str] = mapped_column(Text, nullable=True, default="")
