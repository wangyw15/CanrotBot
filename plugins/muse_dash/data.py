from sqlalchemy import Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from storage import database


class MuseDashAccount(database.Base):
    __tablename__ = "muse_dash_accounts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    player_name: Mapped[str] = mapped_column(Text, nullable=False)
    player_id: Mapped[str] = mapped_column(Text, nullable=False)
