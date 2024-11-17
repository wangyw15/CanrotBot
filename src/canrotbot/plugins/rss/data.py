from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class RssSubscription(database.Base):
    __tablename__ = "rss_subscriptions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    last_update: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # metadata
    title: Mapped[str] = mapped_column(Text, nullable=True)
    link: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # subscriber
    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)


class RssEntry(database.Base):
    __tablename__ = "rss_entries"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    subscription_id: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    guid: Mapped[str] = mapped_column(Text, nullable=False)
    publish_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
