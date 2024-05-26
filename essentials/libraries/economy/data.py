from datetime import datetime
from typing import Optional

from sqlalchemy import Text, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from storage import database


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "economy_accounts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True, unique=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    extra: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")


class Transaction(Base):
    __tablename__ = "economy_transactions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True, unique=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


Base.metadata.create_all(database.get_engine())
