import nonebot.adapters.console as console
import nonebot.adapters.kaiheila as kook
# import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as onebot_v11
import nonebot.adapters.onebot.v12 as onebot_v12
import nonebot.adapters.qq as qq
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    Args,
    Subcommand,
    Query,
    Arparma,
    CommandMeta,
)

from canrotbot.essentials.libraries.model import Platform
from . import data, plugin_manager
from .model import Scope, ACTION, SCOPE, PLATFORM, PLATFORM_ID, PLUGIN_ID, ALL_PLUGINS

plugin_manager_command = Alconna(
    "plugin-manager",
    Subcommand("enable", Args[PLUGIN_ID, str], alias={"启用"}),
    Subcommand("disable", Args[PLUGIN_ID, str], alias={"禁用"}),
    Subcommand("list-disable", alias={"查看禁用"}),
    meta=CommandMeta(description="可以禁用特定插件")
)

__plugin_meta__ = PluginMetadata(
    name="插件管理",
    description=plugin_manager_command.meta.description,
    usage="/plugin <enable|disable|list-disable> [插件名，_all代表所有插件]",
    config=None,
)

plugin_manager_matcher = on_alconna(
    plugin_manager_command,
    aliases={"plugin", "管理插件"},
    block=True,
)

SELF_ID = __name__.split(".")[-1]


@plugin_manager_matcher.handle()
async def _(
    event: console.MessageEvent,
    state: T_State,
):
    state[SCOPE] = Scope.PRIVATE_CHAT
    state[PLATFORM] = Platform.Console
    state[PLATFORM_ID] = str(event.user.id)


@plugin_manager_matcher.handle()
async def _(
    event: qq.C2CMessageCreateEvent,
    state: T_State,
):
    state[SCOPE] = Scope.PRIVATE_CHAT
    state[PLATFORM] = Platform.QQ
    state[PLATFORM_ID] = str(event.get_user_id())


@plugin_manager_matcher.handle()
async def _(
    event: qq.GroupMsgReceiveEvent,
    state: T_State,
):
    state[SCOPE] = Scope.GROUP_CHAT
    state[PLATFORM] = Platform.QQ
    state[PLATFORM_ID] = str(event.group_openid)


@plugin_manager_matcher.handle()
async def _(
    event: qq.GuildMessageEvent,
    state: T_State,
):
    state[SCOPE] = Scope.GROUP_CHAT
    state[PLATFORM] = Platform.QQ
    state[PLATFORM_ID] = str(event.channel_id)


@plugin_manager_matcher.handle()
async def _(
    event: onebot_v11.PrivateMessageEvent,
    state: T_State,
):
    state[SCOPE] = Scope.PRIVATE_CHAT
    state[PLATFORM] = Platform.OneBotV11
    state[PLATFORM_ID] = str(event.get_user_id())


@plugin_manager_matcher.handle()
async def _(
    event: onebot_v11.GroupMessageEvent,
    state: T_State,
):
    state[SCOPE] = Scope.GROUP_CHAT
    state[PLATFORM] = Platform.OneBotV11
    state[PLATFORM_ID] = str(event.group_id)


@plugin_manager_matcher.handle()
async def _(
    event: onebot_v12.PrivateMessageEvent,
    state: T_State,
):
    state[SCOPE] = Scope.PRIVATE_CHAT
    state[PLATFORM] = Platform.OneBotV12
    state[PLATFORM_ID] = str(event.get_user_id())


@plugin_manager_matcher.handle()
async def _(
    event: onebot_v12.GroupMessageEvent,
    state: T_State,
):
    state[SCOPE] = Scope.GROUP_CHAT
    state[PLATFORM] = Platform.OneBotV12
    state[PLATFORM_ID] = str(event.group_id)


# @_plugin_manager_command.assign("enable")
# @_plugin_manager_command.assign("disable")
# @_plugin_manager_command.assign("list-disable")
# async def _(
#     event: mirai2.FriendMessage,
#     state: T_State,
# ):
#     state[SCOPE] = Scope.PRIVATE_CHAT
#     state[PLATFORM] = Platform.Mirai2
#     state[PLATFORM_ID] = str(event.get_user_id())
#
#
# @_plugin_manager_command.assign("enable")
# @_plugin_manager_command.assign("disable")
# @_plugin_manager_command.assign("list-disable")
# async def _(
#     event: mirai2.GroupMessage,
#     state: T_State,
# ):
#     state[SCOPE] = Scope.GROUP_CHAT
#     state[PLATFORM] = Platform.Mirai2
#     state[PLATFORM_ID] = str(event.sender.group.id)


@plugin_manager_matcher.handle()
async def _(
    event: kook.event.ChannelMessageEvent,
    state: T_State,
):
    state[SCOPE] = Scope.GROUP_CHAT
    state[PLATFORM] = Platform.Kook
    state[PLATFORM_ID] = str(event.group_id)


@plugin_manager_matcher.assign("list-disable")
async def _(state: T_State):
    disable_list = "\n".join(
        plugin_manager.list_disabled_plugins(
            state[SCOPE], state[PLATFORM], state[PLATFORM_ID]
        )
    )
    if disable_list:
        await plugin_manager_matcher.finish(f"被禁用的插件:\n{disable_list}")
    else:
        await plugin_manager_matcher.finish(f"没有被禁用的插件")


@plugin_manager_matcher.handle()
async def _(state: T_State, result: Arparma, plugin_id: Query[str] = Query(PLUGIN_ID)):
    if plugin_id.result == SELF_ID:
        await plugin_manager_matcher.finish("不能操作插件管理器")

    display_name = plugin_id.result
    if display_name == ALL_PLUGINS:
        display_name = "所有插件"

    action = ""
    if result.find("enable"):
        if plugin_manager.enable_plugin(
            plugin_id.result, state[SCOPE], state[PLATFORM], state[PLATFORM_ID]
        ):
            action = "启"
        else:
            await plugin_manager_matcher.finish(f"{display_name} 未被禁用")
    elif result.find("disable"):
        if plugin_manager.disable_plugin(
            plugin_id.result, state[SCOPE], state[PLATFORM], state[PLATFORM_ID]
        ):
            action = "禁"
        else:
            await plugin_manager_matcher.finish(f"{display_name} 未被启用")

    if action:
        await plugin_manager_matcher.finish(f"已{action}用 {display_name}")
    else:
        await plugin_manager_matcher.finish("未进行任何操作")


@plugin_manager_matcher.handle()
async def _(state: T_State):
    await plugin_manager_matcher.finish(__plugin_meta__.usage)


def check_self(matcher: Matcher) -> bool:
    return matcher.plugin_id == SELF_ID


@run_preprocessor
async def _(
    event: console.MessageEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.PRIVATE_CHAT
    platform = Platform.Console
    platform_id = str(event.user.id)

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


@run_preprocessor
async def _(
    event: qq.C2CMessageCreateEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.PRIVATE_CHAT
    platform = Platform.QQ
    platform_id = str(event.get_user_id())

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


@run_preprocessor
async def _(
    event: qq.GroupMsgReceiveEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.GROUP_CHAT
    platform = Platform.QQ
    platform_id = str(event.group_openid)

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


@run_preprocessor
async def _(
    event: qq.GuildMessageEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.GROUP_CHAT
    platform = Platform.QQ
    platform_id = str(event.channel_id)

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


@run_preprocessor
async def _(
    event: onebot_v11.PrivateMessageEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.PRIVATE_CHAT
    platform = Platform.OneBotV11
    platform_id = str(event.get_user_id())

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


@run_preprocessor
async def _(
    event: onebot_v11.GroupMessageEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.GROUP_CHAT
    platform = Platform.OneBotV11
    platform_id = str(event.group_id)

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


@run_preprocessor
async def _(
    event: onebot_v12.PrivateMessageEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.PRIVATE_CHAT
    platform = Platform.OneBotV12
    platform_id = str(event.get_user_id())

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


@run_preprocessor
async def _(
    event: onebot_v12.GroupMessageEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.GROUP_CHAT
    platform = Platform.OneBotV12
    platform_id = str(event.group_id)

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()


# @run_preprocessor
# async def _(
#     event: mirai2.FriendMessage,
#     matcher: Matcher,
# ):
#     # 不禁用自己
#     if matcher.plugin_id == __name__.split(".")[-1]:
#         return
#
#     scope = Scope.PRIVATE_CHAT
#     platform = Platform.Mirai2
#     platform_id = str(event.get_user_id())
#
#     disabled_plugins = plugin_manager.list_disabled_plugins(
#         scope, platform, platform_id
#     )
#     if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
#         await matcher.finish()
#
#
# @run_preprocessor
# async def _(
#     event: mirai2.GroupMessage,
#     matcher: Matcher,
# ):
#     # 不禁用自己
#     if matcher.plugin_id == __name__.split(".")[-1]:
#         return
#
#     scope = Scope.GROUP_CHAT
#     platform = Platform.Mirai2
#     platform_id = str(event.sender.group.id)
#
#     disabled_plugins = plugin_manager.list_disabled_plugins(
#         scope, platform, platform_id
#     )
#     if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
#         await matcher.finish()


@run_preprocessor
async def _(
    event: kook.event.ChannelMessageEvent,
    matcher: Matcher,
):
    # 不禁用自己
    if matcher.plugin_id == __name__.split(".")[-1]:
        return

    scope = Scope.GROUP_CHAT
    platform = Platform.Kook
    platform_id = str(event.group_id)

    disabled_plugins = plugin_manager.list_disabled_plugins(
        scope, platform, platform_id
    )
    if ALL_PLUGINS in disabled_plugins or matcher.plugin_id in disabled_plugins:
        await matcher.finish()
