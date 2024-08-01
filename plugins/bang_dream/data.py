from datetime import datetime

from sqlalchemy import Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class History(database.Base):
    __tablename__ = "bang_dream_gacha_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    gacha: Mapped[str] = mapped_column(Text, nullable=False)
    cards: Mapped[str] = mapped_column(Text, nullable=False)
