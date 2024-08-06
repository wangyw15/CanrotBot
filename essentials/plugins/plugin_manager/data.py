from sqlalchemy import Boolean, Integer, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from essentials.libraries.model import Platform
from ...libraries import database
from .model import Scope


class PluginManagementData(database.Base):
    __tablename__ = "plugin_manager_plugins_data"

    id: Mapped[int] = mapped_column(
        Integer, nullable=False, primary_key=True, unique=True, autoincrement=True
    )
    plugin_id: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[Scope] = mapped_column(Enum(Scope), nullable=False)
    platform: Mapped[Platform] = mapped_column(Enum(Platform), nullable=False)
    platform_id: Mapped[str] = mapped_column(Text, nullable=False)
    enable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
