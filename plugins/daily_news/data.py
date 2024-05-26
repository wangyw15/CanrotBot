from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from storage import database


class Base(DeclarativeBase):
    pass


class Subscribers(Base):
    __tablename__ = "daily_news_subscribers"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    group_id: Mapped[str] = mapped_column(Text, nullable=False)
    bot: Mapped[str] = mapped_column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
