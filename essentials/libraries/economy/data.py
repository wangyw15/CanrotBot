from datetime import datetime
from typing import Optional

from sqlalchemy import Text, Float, DateTime, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from essentials.libraries import database


class Account(database.Base):
    __tablename__ = "economy_accounts"

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False, unique=True
    )
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    extra: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="")


class Transaction(database.Base):
    __tablename__ = "economy_transactions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True, unique=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    balance: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extra: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
