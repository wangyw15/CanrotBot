from sqlalchemy import Column, Text
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class MuseDashAccount(Base):
    __tablename__ = 'muse_dash_accounts'

    user_id: Mapped[str] = Column(Text, nullable=False, primary_key=True, unique=True)
    player_name: Mapped[str] = Column(Text, nullable=False)
    player_id: Mapped[str] = Column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
