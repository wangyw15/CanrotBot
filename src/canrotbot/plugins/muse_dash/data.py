from sqlalchemy import Text, Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class MuseDashAccount(database.Base):
    __tablename__ = "muse_dash_accounts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    player_name: Mapped[str] = mapped_column(Text, nullable=False)
    player_id: Mapped[str] = mapped_column(Text, nullable=False)
