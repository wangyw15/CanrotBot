from datetime import datetime

from sqlalchemy import Text, DateTime, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from storage import database


class Base(DeclarativeBase):
    pass


class SigninRecord(Base):
    __tablename__ = "signin"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<SigninRecord(uid={self.user_id}, time={self.time}, title={self.title}, content={self.content})>"


Base.metadata.create_all(database.get_engine())
