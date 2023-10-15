from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped

from storage import database


class Base(DeclarativeBase):
    pass


class CommercialPerformance(Base):
    __tablename__ = 'commercial_performances'

    id: Mapped[str] = Column(String, primary_key=True, nullable=False, unique=True)
    acceptance_id: Mapped[str] = Column(String, nullable=True)
    approval_id: Mapped[str] = Column(String, nullable=True)
    permit_id: Mapped[str] = Column(String, nullable=True)
    original_approval_id: Mapped[str] = Column(String, nullable=True)
    license_matter: Mapped[str] = Column(String, nullable=True)

    organizer: Mapped[str] = Column(String, nullable=True)
    name: Mapped[str] = Column(String, nullable=True)
    date: Mapped[str] = Column(String, nullable=True)
    address: Mapped[str] = Column(String, nullable=True)
    actor_count: Mapped[int] = Column(Integer, nullable=True)
    session_number: Mapped[int] = Column(Integer, nullable=True)
    foreigner_short_term: Mapped[bool] = Column(Boolean, nullable=True)
    content: Mapped[str] = Column(String, nullable=True)


class PerformanceActors(Base):
    __tablename__ = 'commercial_performance_actors'

    performance_id: Mapped[str] = Column(String, primary_key=True, nullable=False)
    id: Mapped[int] = Column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = Column(String, nullable=True)
    gender: Mapped[str] = Column(String, nullable=True)
    region: Mapped[str] = Column(String, nullable=True)
    license_numer: Mapped[str] = Column(String, nullable=True)


Base.metadata.create_all(database.get_engine())
