from datetime import datetime

from sqlalchemy import Column, Text, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class SigninRecord(Base):
    __tablename__ = "signin"

    user_id: Mapped[str] = Column(Text, nullable=False, primary_key=True)
    time: Mapped[datetime] = Column(DateTime, primary_key=True, nullable=False)
    title: Mapped[str] = Column(Text, nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<SigninRecord(uid={self.user_id}, time={self.time}, title={self.title}, content={self.content})>"


Base.metadata.create_all(database.get_engine())
