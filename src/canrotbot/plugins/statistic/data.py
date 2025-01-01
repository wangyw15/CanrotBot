from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class MessageHistory(database.Base):
    __tablename__ = "statistic_message_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    # sender
    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[str] = mapped_column(Text, nullable=True)
    target_id: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    """
    Event.get_user_id()
    """


class PluginHistory(database.Base):
    __tablename__ = "statistic_plugin_history"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    plugin_name: Mapped[str] = mapped_column(Text, nullable=False)
    module_name: Mapped[str] = mapped_column(Text, nullable=False)
    command: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    # sender
    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[str] = mapped_column(Text, nullable=True)
    target_id: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    """
    Event.get_user_id()
    """
