from sqlalchemy import Boolean, Enum, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database

from .model import ReplyMode


class ReplyGroupSettings(database.Base):
    __tablename__ = "reply_group_settings"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )

    # target
    # private_chat应该常为False，避免与LLM插件冲突
    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)

    # 通用配置
    rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.05)
    mode: Mapped[ReplyMode] = mapped_column(
        Enum(ReplyMode), nullable=False, default=ReplyMode.ARRISA
    )

    # LLM
    system_prompt: Mapped[str] = mapped_column(Text, nullable=True)
