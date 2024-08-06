from sqlalchemy import Text, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from essentials.libraries import file, path, database


class Investigator(database.Base):
    __tablename__ = "trpg_investigators"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    owner_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

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


class PlayerData(database.Base):
    __tablename__ = "trpg_player_data"

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, nullable=False, unique=True
    )
    group_id: Mapped[str] = mapped_column(Text, nullable=False)
    selected_investigator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Investigator.id), nullable=True
    )
    extra: Mapped[str] = mapped_column(Text, nullable=True, default="")


class AdditionalProperty(database.Base):
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


class Skill(database.Base):
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


class Status(database.Base):
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


class Item(database.Base):
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


TRPG_ASSET_PATH = path.get_asset_path("trpg")
TRPG_BASIC_PROPERTIES: dict = file.read_json(TRPG_ASSET_PATH / "basic_properties.json")
