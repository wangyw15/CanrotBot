from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class Subscribers(database.Base):
    __tablename__ = "daily_news_subscribers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    group_id: Mapped[str] = mapped_column(Text, nullable=False)
    bot: Mapped[str] = mapped_column(Text, nullable=False)
