from sqlalchemy import Column, Text
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class Bind(Base):
    __tablename__ = "user_binds"
    platform_user_id: Mapped[str] = Column(
        Text, primary_key=True, nullable=False, unique=True
    )
    user_id: Mapped[str] = Column(Text, nullable=False)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = Column(Text, primary_key=True, nullable=False, unique=True)
    extra: Mapped[str] = Column(Text, nullable=True)


Base.metadata.create_all(database.get_engine())
