from sqlalchemy import Column, Text, Boolean, Float
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class ReplyConfig(Base):
    __tablename__ = "reply"

    group_id: Mapped[str] = Column(Text, nullable=False, primary_key=True, unique=True)
    enable: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    rate: Mapped[float] = Column(Float, nullable=False, default=0)


Base.metadata.create_all(database.get_engine())
