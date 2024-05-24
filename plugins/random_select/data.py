from sqlalchemy import Integer, Column, Text
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class RandomSelectPreset(Base):
    __tablename__ = "random_select_preset"

    id: Mapped[int] = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False, unique=True
    )
    name: Mapped[str] = Column(Text, nullable=False, unique=True)
    items: Mapped[str] = Column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
