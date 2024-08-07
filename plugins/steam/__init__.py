import typing

from arclet.alconna import Args
from nonebot import get_plugin_config, on_regex
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    AlconnaQuery,
    Query,
    UniMessage,
    Text,
    Image,
)

from essentials.libraries import util
from . import steam
from .config import SteamConfig

__plugin_meta__ = PluginMetadata(
    name="Steam助手",
    description="现在只能根据 appid 查询信息",
    usage="/<steam|sbeam|蒸汽|蒸汽平台> <appid>",
    config=SteamConfig,
)

_steam_config = get_plugin_config(SteamConfig)


async def _generate_message(app_info: dict) -> UniMessage:
    header_img: str = app_info["header_image"]
    bg_img: str = app_info["background_raw"]

    name: str = app_info["name"]
    appid: int = app_info["steam_appid"]
    desc: str = app_info["short_description"]
    coming_soon: bool = app_info["release_date"]["coming_soon"]
    release_date: str = app_info["release_date"]["date"]
    developers: list[str] = app_info["developers"]
    publishers: list[str] = app_info["publishers"]
    genres: list[str] = [x["description"] for x in app_info["genres"]]
    categories: list[str] = [x["description"] for x in app_info["categories"]]
    initial_price: str = app_info["price_overview"]["initial_formatted"]
    final_price: str = app_info["price_overview"]["final_formatted"]
    discount_percentage: int = app_info["price_overview"]["discount_percent"]

    txt_msg = f"""
名称: {name}
发布时间: {'待发售' if coming_soon else release_date}
开发商: {', '.join(developers)}
发行商: {', '.join(publishers)}
类型: {', '.join(genres)}
分类: {', '.join(categories)}
简介: {desc}
    """.strip()

    if discount_percentage != 0:
        txt_msg += f"\n原价: {initial_price}\n现价: {final_price}\n折扣: {discount_percentage}%"
    else:
        txt_msg += f"\n价格: {final_price}"

    txt_msg += f"\n链接: https://store.steampowered.com/app/{appid}"

    ret = UniMessage()
    if await util.can_send_segment(Image):
        ret.append(Image(header_img))
    ret.append(Text(txt_msg))
    if await util.can_send_segment(Image):
        ret.append(Image(bg_img))
    return ret


_steam_command_handler = on_alconna(
    Alconna(
        "steam",
        Args["appid", str],
    ),
    block=True,
)


@_steam_command_handler.handle()
async def _(appid: Query[str] = AlconnaQuery("appid")):
    appid = appid.result.strip()
    if appid.isdigit():
        if appinfo := await steam.fetch_app_info(
            appid, _steam_config.language, _steam_config.region
        ):
            if appinfo.get(appid, {}).get("success", False):
                appinfo = appinfo[appid]["data"]
                await _steam_command_handler.finish(await _generate_message(appinfo))
            else:
                await _steam_command_handler.finish("未找到该游戏")
        else:
            await _steam_command_handler.finish("请求失败")
    else:
        await _steam_command_handler.finish("请输入正确的游戏ID")


_steam_link_handler = on_regex(
    r"(?:https?:\/\/)?store\.steampowered\.com\/app\/(\d+)", block=True
)


@_steam_link_handler.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    appid = reg[0]
    if appinfo := await steam.fetch_app_info(
        appid, _steam_config.language, _steam_config.region
    ):
        if appinfo.get(appid, {}).get("success", False):
            appinfo = appinfo[appid]["data"]
            await _steam_link_handler.finish(
                await (await _generate_message(appinfo)).export()
            )
