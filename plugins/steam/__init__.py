import typing

from nonebot import get_plugin_config, on_regex
from nonebot.adapters.qq import Event as QQEvent
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    Query,
    Args,
    CommandMeta,
)

from . import steam
from .config import SteamConfig

__plugin_meta__ = PluginMetadata(
    name="Steam 助手",
    description="现在只能根据 appid 查询信息",
    usage="/<steam> <appid>\n发送Steam 链接也会自动触发",
    config=SteamConfig,
)

_steam_config = get_plugin_config(SteamConfig)

steam_command_matcher = on_alconna(
    Alconna(
        "steam",
        Args["appid", str],
        meta=CommandMeta(description="根据 appid 查询 Steam 游戏信息"),
    ),
    block=True,
)

steam_link_matcher = on_regex(
    r"(?:https?:\/\/)?store\.steampowered\.com\/app\/(\d+)", block=True
)


@steam_command_matcher.handle()
async def command_set_state(state: T_State, appid: Query[str] = Query("appid")):
    appid = appid.result.strip()
    if appid.isdigit():
        state["appid"] = appid
        # state["triggered_by"] = "command"
    else:
        await steam_command_matcher.finish("请输入正确的游戏ID")


@steam_link_matcher.handle()
async def link_set_state(
    state: T_State, reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]
):
    appid: str = reg[0]
    if appid.isdigit():
        state["appid"] = appid
        # state["triggered_by"] = "link"


@steam_command_matcher.handle()
@steam_link_matcher.handle()
async def set_official_qq_state(event: QQEvent, state: T_State):
    # do not remove event parameter, it's necessary to decide whether to send url
    event.get_user_id()  # just to make event used, meaningless
    state["official_qq"] = True


@steam_command_matcher.handle()
@steam_link_matcher.handle()
async def send_game_info(state: T_State):
    appid: str = state["appid"]
    if appinfo := await steam.fetch_app_info(
        appid, _steam_config.language, _steam_config.region
    ):
        if appinfo.get(appid, {}).get("success", False):
            appinfo = appinfo[appid]["data"]
            await steam_command_matcher.finish(
                await steam.generate_message(
                    appinfo, with_url=not state.get("official_qq", False)
                )
            )
        else:
            await steam_command_matcher.finish(
                f"未在 Steam {_steam_config.region} 区域找到该游戏"
            )
    else:
        await steam_command_matcher.finish("Steam 请求失败")
