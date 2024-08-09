from typing import cast

from sqlalchemy import select, insert, delete, ColumnElement

from essentials.libraries.model import Platform
from .data import PluginManagementData
from .model import Scope
from ...libraries import database


def list_disabled_plugins(
    scope: Scope, platform: Platform, platform_id: str
) -> list[str]:
    with database.get_session().begin() as session:
        result = (
            session.execute(
                select(PluginManagementData.plugin_id)
                .where(cast(ColumnElement[bool], PluginManagementData.scope == scope))
                .where(
                    cast(ColumnElement[bool], PluginManagementData.platform == platform)
                )
                .where(
                    cast(
                        ColumnElement[bool],
                        PluginManagementData.platform_id == platform_id,
                    )
                )
                .where(cast(ColumnElement[bool], PluginManagementData.enable == False))
            )
            .scalars()
            .all()
        )
        return [name for name in result]


def enable_plugin(
    plugin_id: str, scope: Scope, platform: Platform, platform_id: str
) -> bool:
    with database.get_session().begin() as session:
        if plugin_id in list_disabled_plugins(scope, platform, platform_id):
            session.execute(
                delete(PluginManagementData)
                .where(
                    cast(
                        ColumnElement[bool], PluginManagementData.plugin_id == plugin_id
                    )
                )
                .where(cast(ColumnElement[bool], PluginManagementData.scope == scope))
                .where(
                    cast(ColumnElement[bool], PluginManagementData.platform == platform)
                )
                .where(
                    cast(
                        ColumnElement[bool],
                        PluginManagementData.platform_id == platform_id,
                    )
                )
                .where(cast(ColumnElement[bool], PluginManagementData.enable == False))
            )
            session.commit()
            return True
    return False


def disable_plugin(
    plugin_id: str, scope: Scope, platform: Platform, platform_id: str
) -> bool:
    with database.get_session().begin() as session:
        if plugin_id not in list_disabled_plugins(scope, platform, platform_id):
            session.execute(
                insert(PluginManagementData).values(
                    plugin_id=plugin_id,
                    scope=scope,
                    platform=platform,
                    platform_id=platform_id,
                    enable=False,
                )
            )
            session.commit()
            return True
    return False


__all__ = [
    "list_disabled_plugins",
    "enable_plugin",
    "disable_plugin",
]
