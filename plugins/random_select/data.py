from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class RandomSelectPreset(database.Base):
    __tablename__ = "random_select_preset"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    items: Mapped[str] = mapped_column(Text, nullable=False)
