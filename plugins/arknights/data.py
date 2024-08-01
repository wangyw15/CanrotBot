from datetime import datetime

from sqlalchemy import Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class Statistics(database.Base):
    __tablename__ = "arknights_gacha_statistics"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    three_stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    four_stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    five_stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    six_stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    times: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_six_star: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class History(database.Base):
    __tablename__ = "arknights_gacha_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    operators: Mapped[str] = mapped_column(Text, nullable=False)
