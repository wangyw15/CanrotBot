from datetime import datetime

from sqlalchemy import Integer, Column, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class BaiduAccount(Base):
    __tablename__ = "baidu_account"

    id: Mapped[int] = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    owner: Mapped[str] = Column(Text, nullable=False)
    bduss: Mapped[str] = Column(Text, nullable=False)
    stoken: Mapped[str] = Column(Text, nullable=False)
    alias: Mapped[str] = Column(Text, nullable=True, default="")


class TiebaSignResultSubscriber(Base):
    __tablename__ = "tieba_sign_result_subscriber"

    id: Mapped[int] = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    account_id: Mapped[int] = Column(
        Integer, ForeignKey("baidu_account.id"), nullable=False
    )
    puid: Mapped[str] = Column(Text, nullable=False)
    bot: Mapped[str] = Column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
