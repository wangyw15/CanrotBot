from sqlalchemy import BigInteger, Boolean, Enum, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database

from .model import SessionMode


class LLMContext(database.Base):
    __tablename__ = "llm_context"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    # owner
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # data
    name: Mapped[str] = mapped_column(Text, nullable=True, default="")
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)


class LLMSessionMode(database.Base):
    __tablename__ = "llm_session_mode"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )

    # target
    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)

    mode: Mapped[SessionMode] = mapped_column(Enum(SessionMode), nullable=False)
