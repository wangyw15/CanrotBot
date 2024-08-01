from sqlalchemy import Integer, Text, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class BaiduAccount(database.Base):
    __tablename__ = "baidu_account"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    owner_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bduss: Mapped[str] = mapped_column(Text, nullable=False)
    stoken: Mapped[str] = mapped_column(Text, nullable=False)
    alias: Mapped[str] = mapped_column(Text, nullable=True, default="")


class TiebaSignResultSubscriber(database.Base):
    __tablename__ = "tieba_sign_result_subscriber"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(BaiduAccount.id), nullable=False
    )
    puid: Mapped[str] = mapped_column(Text, nullable=False)
    bot: Mapped[str] = mapped_column(Text, nullable=False)
