from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class Webhook(database.Base):
    __tablename__ = "webhook_hooks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    token: Mapped[str] = mapped_column(Text, nullable=False)
    template_name: Mapped[str] = mapped_column(Text, nullable=False)

    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)
