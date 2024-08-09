from sqlalchemy import Text, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from essentials.libraries import database


class User(database.Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False, unique=True
    )
    extra: Mapped[str] = mapped_column(Text, nullable=True)


class Bind(database.Base):
    __tablename__ = "user_binds"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    extra: Mapped[str] = mapped_column(Text, nullable=True)
