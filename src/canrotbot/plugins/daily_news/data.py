from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class Subscribers(database.Base):
    __tablename__ = "daily_news_subscribers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )

    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)
