from datetime import datetime

from sqlalchemy import BigInteger, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class GachaHistory(database.Base):
    __tablename__ = "arknights_gacha_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )


class GachaHistoryOperators(database.Base):
    __tablename__ = "arknights_gacha_operators"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    gacha_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    operator_id: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[int] = mapped_column(Integer, nullable=False)
