from sqlalchemy import Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database
from canrotbot.essentials.libraries.model import ChatType


class Webhook(database.Base):
    __tablename__ = "webhook_hooks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    token: Mapped[str] = mapped_column(Text, nullable=False)
    template_name: Mapped[str] = mapped_column(Text, nullable=False)

    chat_type: Mapped[ChatType] = mapped_column(
        Enum(ChatType), nullable=False, default=ChatType.Private
    )
    bot_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)
