from datetime import datetime

from sqlalchemy import Integer, Column, Text, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class Statistics(Base):
    __tablename__ = 'arknights_gacha_statistics'

    user_id: Mapped[str] = Column(Text, primary_key=True, nullable=False, unique=True)
    three_stars: Mapped[int] = Column(Integer, nullable=False, default=0)
    four_stars: Mapped[int] = Column(Integer, nullable=False, default=0)
    five_stars: Mapped[int] = Column(Integer, nullable=False, default=0)
    six_stars: Mapped[int] = Column(Integer, nullable=False, default=0)
    times: Mapped[int] = Column(Integer, nullable=False, default=0)
    last_six_star: Mapped[int] = Column(Integer, nullable=False, default=0)


class History(Base):
    __tablename__ = 'arknights_gacha_history'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    user_id: Mapped[str] = Column(Text, nullable=False)
    time: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.now)
    operators: Mapped[str] = Column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
