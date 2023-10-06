import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Column, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class CommentType(enum.Enum):
    anime = 'anime'


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    type: Mapped[CommentType] = Column(Enum(CommentType), nullable=False)
    time: Mapped[Optional[datetime]] = Column(DateTime, nullable=True, default=datetime.now)
    title: Mapped[str] = Column(Text, nullable=False)
    author: Mapped[Optional[str]] = Column(Text, nullable=True)
    content: Mapped[str] = Column(Text, nullable=False)
    nickname: Mapped[Optional[str]] = Column(Text, nullable=True)


Base.metadata.create_all(database.get_engine())
