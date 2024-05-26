from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from storage import database


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    extra: Mapped[str] = mapped_column(Text, nullable=True)


class Bind(Base):
    __tablename__ = "user_binds"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    platform_user_id: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    extra: Mapped[str] = mapped_column(Text, nullable=True)


Base.metadata.create_all(database.get_engine())
