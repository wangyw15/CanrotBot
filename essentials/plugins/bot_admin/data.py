from sqlalchemy import Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class GroupConfig(database.Base):
    __tablename__ = "group_configs"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, unique=True, autoincrement=True
    )
    group_id: Mapped[str] = mapped_column(Text, nullable=False)
    enable_bot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    disabled_plugins: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
