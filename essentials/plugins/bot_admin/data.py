from sqlalchemy import Column, Text, Boolean
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import database


class Base(DeclarativeBase):
    pass


class GroupConfig(Base):
    __tablename__ = 'group_configs'

    group_id: Mapped[str] = Column(Text, nullable=False, primary_key=True, unique=True)
    enable_bot: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    disabled_plugins: Mapped[str] = Column(Text, nullable=False, default='[]')


Base.metadata.create_all(database.get_engine())
