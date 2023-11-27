from sqlalchemy import Column, Text
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class Subscribers(Base):
    __tablename__ = "daily_news_subscribers"

    group_id: Mapped[str] = Column(Text, primary_key=True, nullable=False)
    bot: Mapped[str] = Column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
