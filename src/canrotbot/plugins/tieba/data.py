from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database

from .model import ForumSigninResultType


class Account(database.Base):
    __tablename__ = "baidu_account"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    owner_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bduss: Mapped[str] = mapped_column(Text, nullable=False)
    stoken: Mapped[str] = mapped_column(Text, nullable=False)
    alias: Mapped[str] = mapped_column(Text, nullable=True, default="")


class ForumSigninResultList(database.Base):
    __tablename__ = "tieba_signin_result_list"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Account.id), nullable=False
    )
    time: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )


class ForumSigninResultData(database.Base):
    __tablename__ = "tieba_signin_result_data"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    signin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ForumSigninResultList.id), nullable=False
    )
    code: Mapped[ForumSigninResultType] = mapped_column(
        Enum(ForumSigninResultType), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rank: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")


class SigninResultSubscriber(database.Base):
    __tablename__ = "tieba_signin_result_subscriber"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Account.id), nullable=False
    )

    private_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    channel_chat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_id: Mapped[str] = mapped_column(Text, nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)
