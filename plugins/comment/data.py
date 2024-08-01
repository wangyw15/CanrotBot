import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class CommentType(enum.Enum):
    anime = "anime"


class Comment(database.Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(Text, nullable=False)
    type: Mapped[CommentType] = mapped_column(Enum(CommentType), nullable=False)
    time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, default=datetime.now
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    nickname: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
