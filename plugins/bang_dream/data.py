from datetime import datetime

from sqlalchemy import Integer, Column, Text, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class History(Base):
    __tablename__ = "bang_dream_gacha_history"

    id: Mapped[int] = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    user_id: Mapped[str] = Column(Text, nullable=False)
    time: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.now)
    gacha: Mapped[str] = Column(Text, nullable=False)
    cards: Mapped[str] = Column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
