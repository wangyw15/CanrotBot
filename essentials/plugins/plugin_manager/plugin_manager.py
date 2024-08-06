from sqlalchemy import select, insert, delete

from essentials.libraries.model import Platform
from ...libraries import database
from .data import PluginManagementData
from .model import Scope


def list_disabled_plugins(
    scope: Scope, platform: Platform, platform_id: str
) -> list[str]:
    with database.get_session().begin() as session:
        result = (
            session.execute(
                select(PluginManagementData.plugin_id)
                .where(PluginManagementData.scope.is_(scope))
                .where(PluginManagementData.platform.is_(platform))
                .where(PluginManagementData.platform_id.is_(platform_id))
                .where(PluginManagementData.enable.is_(False))
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
                .where(PluginManagementData.plugin_id.is_(plugin_id))
                .where(PluginManagementData.scope.is_(scope))
                .where(PluginManagementData.platform.is_(platform))
                .where(PluginManagementData.platform_id.is_(platform_id))
                .where(PluginManagementData.enable.is_(False))
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
