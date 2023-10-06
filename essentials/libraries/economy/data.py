from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = 'economy_accounts'

    user_id: Mapped[str] = Column(Text, primary_key=True, nullable=False, unique=True)
    balance: Mapped[float] = Column(Float, nullable=False, default=0)


class Record(Base):
    __tablename__ = 'economy_records'

    transaction_id: Mapped[int] = Column(Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    user_id: Mapped[str] = Column(Text, nullable=False)
    time: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.now)
    amount: Mapped[float] = Column(Float, nullable=False)
    balance: Mapped[float] = Column(Float, nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)
    extra: Mapped[Optional[str]] = Column(Text, nullable=True)


Base.metadata.create_all(database.get_engine())
