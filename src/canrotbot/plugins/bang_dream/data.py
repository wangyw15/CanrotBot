from datetime import datetime

from sqlalchemy import BigInteger, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class GachaHistory(database.Base):
    __tablename__ = "bang_dream_gacha_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    gacha_id: Mapped[int] = mapped_column(Integer, nullable=False)


class GachaHistoryCards(database.Base):
    __tablename__ = "bang_dream_gacha_history_cards"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    gacha_history_id: Mapped[int] = mapped_column(Integer, nullable=False)
    character_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    card_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rarity: Mapped[int] = mapped_column(Integer, nullable=False)
    attribute: Mapped[str] = mapped_column(Text, nullable=False)
