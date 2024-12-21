from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class LLMContext(database.Base):
    __tablename__ = "llm_context"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    # owner
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # data
    name: Mapped[str] = mapped_column(Text, nullable=True, default="")
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)
