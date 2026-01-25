from sqlalchemy import Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from canrotbot.essentials.libraries import database


class CommercialPerformance(database.Base):
    __tablename__ = "commercial_performances"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True, unique=True
    )
    performance_id: Mapped[str] = mapped_column(Text, nullable=False)
    acceptance_id: Mapped[str] = mapped_column(Text, nullable=True)
    approval_id: Mapped[str] = mapped_column(Text, nullable=True)
    permit_id: Mapped[str] = mapped_column(Text, nullable=True)
    original_approval_id: Mapped[str] = mapped_column(Text, nullable=True)
    license_matter: Mapped[str] = mapped_column(Text, nullable=True)

    organizer: Mapped[str] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    actor_count: Mapped[int] = mapped_column(Integer, nullable=True)
    session_number: Mapped[int] = mapped_column(Integer, nullable=True)
    foreigner_short_term: Mapped[bool] = mapped_column(Boolean, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)


class PerformanceActors(database.Base):
    __tablename__ = "commercial_performance_actors"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, autoincrement=True, unique=True
    )
    performance_id: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    gender: Mapped[str] = mapped_column(Text, nullable=True)
    region: Mapped[str] = mapped_column(Text, nullable=True)
    license_number: Mapped[str] = mapped_column(Text, nullable=True)
