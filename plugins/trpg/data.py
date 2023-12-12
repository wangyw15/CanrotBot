from sqlalchemy import Column, Text, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase

from storage import asset, database


class Base(DeclarativeBase):
    pass


class PlayerData(Base):
    __tablename__ = "trpg_player_data"

    user_id: Mapped[str] = Column(Text, primary_key=True, nullable=False)
    group_id: Mapped[str] = Column(Text, primary_key=True, nullable=False)
    selected_investigator_id: Mapped[int] = Column(Integer, nullable=True)
    extra: Mapped[str] = Column(Text, nullable=True, default="")


class Investigator(Base):
    __tablename__ = "trpg_investigators"

    investigator_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    owner_user_id: Mapped[str] = Column(Text, nullable=False)

    name: Mapped[str] = Column(Text, nullable=False, default="")
    age: Mapped[int] = Column(Integer, nullable=False, default="")
    gender: Mapped[str] = Column(Text, nullable=False, default="")
    birthplace: Mapped[str] = Column(Text, nullable=False, default="")
    profession: Mapped[str] = Column(Text, nullable=False, default="")

    strength: Mapped[int] = Column(Integer, nullable=False, default=0)
    constitution: Mapped[int] = Column(Integer, nullable=False, default=0)
    dexterity: Mapped[int] = Column(Integer, nullable=False, default=0)
    appearance: Mapped[int] = Column(Integer, nullable=False, default=0)
    power: Mapped[int] = Column(Integer, nullable=False, default=0)
    intelligence: Mapped[int] = Column(Integer, nullable=False, default=0)
    size: Mapped[int] = Column(Integer, nullable=False, default=0)
    education: Mapped[int] = Column(Integer, nullable=False, default=0)
    luck: Mapped[int] = Column(Integer, nullable=False, default=0)

    extra: Mapped[str] = Column(Text, nullable=True, default="")


class AdditionalProperty(Base):
    __tablename__ = "trpg_additional_properties"

    investigator_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )

    name: Mapped[str] = Column(Text, nullable=False, default="")
    value: Mapped[int] = Column(Integer, nullable=False, default=0)
    description: Mapped[str] = Column(Text, nullable=True, default="")


class Skill(Base):
    __tablename__ = "trpg_skills"

    investigator_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )

    name: Mapped[str] = Column(Text, nullable=False, default="")
    value: Mapped[int] = Column(Integer, nullable=False, default=0)
    description: Mapped[str] = Column(Text, nullable=True, default="")


class Status(Base):
    __tablename__ = "trpg_status"

    investigator_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )

    name: Mapped[str] = Column(Text, nullable=False, default="")
    value: Mapped[int] = Column(Integer, nullable=False, default=0)
    description: Mapped[str] = Column(Text, nullable=True, default="")


class Item(Base):
    __tablename__ = "trpg_items"

    investigator_id: Mapped[int] = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )

    name: Mapped[str] = Column(Text, nullable=False, default="")
    description: Mapped[str] = Column(Text, nullable=True, default="")
    effect: Mapped[str] = Column(Text, nullable=True, default="")


Base.metadata.create_all(database.get_engine())

trpg_assets = asset.AssetManager("trpg")
