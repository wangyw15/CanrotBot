from sqlalchemy import Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column

from storage import asset, database


class Base(DeclarativeBase):
    pass


class Investigator(Base):
    __tablename__ = "trpg_investigators"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    owner_user_id: Mapped[str] = mapped_column(Text, nullable=False)

    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    age: Mapped[int] = mapped_column(Integer, nullable=False, default="")
    gender: Mapped[str] = mapped_column(Text, nullable=False, default="")
    birthplace: Mapped[str] = mapped_column(Text, nullable=False, default="")
    profession: Mapped[str] = mapped_column(Text, nullable=False, default="")

    strength: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    constitution: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dexterity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    appearance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    power: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    intelligence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    education: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    luck: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    extra: Mapped[str] = mapped_column(Text, nullable=True, default="")


class PlayerData(Base):
    __tablename__ = "trpg_player_data"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(Text, nullable=False)
    group_id: Mapped[str] = mapped_column(Text, nullable=False)
    selected_investigator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Investigator.id), nullable=True
    )
    extra: Mapped[str] = mapped_column(Text, nullable=True, default="")


class AdditionalProperty(Base):
    __tablename__ = "trpg_additional_properties"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    investigator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Investigator.id), nullable=False
    )

    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")


class Skill(Base):
    __tablename__ = "trpg_skills"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    investigator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Investigator.id), nullable=False
    )

    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")


class Status(Base):
    __tablename__ = "trpg_status"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    investigator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Investigator.id), nullable=False
    )

    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")


class Item(Base):
    __tablename__ = "trpg_items"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    investigator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Investigator.id), nullable=False
    )

    name: Mapped[str] = mapped_column(Text, nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    effect: Mapped[str] = mapped_column(Text, nullable=True, default="")


Base.metadata.create_all(database.get_engine())

trpg_assets = asset.AssetManager("trpg")
