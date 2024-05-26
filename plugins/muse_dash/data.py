from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from storage import database


class Base(DeclarativeBase):
    pass


class MuseDashAccount(Base):
    __tablename__ = "muse_dash_accounts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    player_name: Mapped[str] = mapped_column(Text, nullable=False)
    player_id: Mapped[str] = mapped_column(Text, nullable=False)


Base.metadata.create_all(database.get_engine())
