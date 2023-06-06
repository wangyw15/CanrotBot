from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from pydantic import BaseModel, validator

from ..libraries.link_metadata import fetch_steam_app_info
from ..adapters import unified

__plugin_meta__ = PluginMetadata(
    name='Steam助手',
    description='现在只能根据 appid 查询信息',
    usage='/<steam|sbeam|蒸汽|蒸汽平台> <appid>',
    config=None
)


class SteamConfig(BaseModel):
    """
    Steam插件配置
    """
    steam_region: str = 'cn'
    steam_language: str = 'zh-cn'
    
    @validator('steam_region')
    def steam_region_validator(cls, v):
        if (not isinstance(v, str)) or (not v):
            raise ValueError('steam_region must be a str')
        return v
    
    @validator('steam_language')
    def steam_language_validator(cls, v):
        if (not isinstance(v, str)) or (not v):
            raise ValueError('steam_language must be a str')
        return v


_steam_config = SteamConfig.parse_obj(get_driver().config)


def _generate_message(app_info: dict) -> str:
    name: str = app_info['name']
    appid: int = app_info['steam_appid']
    desc: str = app_info['short_description']
    coming_soon: bool = app_info['release_date']['coming_soon']
    release_date: str = app_info['release_date']['date']
    developers: list[str] = app_info['developers']
    publishers: list[str] = app_info['publishers']
    genres: list[str] = [x['description'] for x in app_info['genres']]
    categories: list[str] = [x['description'] for x in app_info['categories']]
    initial_price: str = app_info['price_overview']['initial_formatted']
    final_price: str = app_info['price_overview']['final_formatted']
    discount_percentage: int = app_info['price_overview']['discount_percent']

    ret = f"""
名称: {name}
发布时间: {'待发售' if coming_soon else release_date}
开发商: {', '.join(developers)}
发行商: {', '.join(publishers)}
类型: {', '.join(genres)}
分类: {', '.join(categories)}
简介: {desc}
    """.strip()

    if discount_percentage != 0:
        ret += f'\n原价: {initial_price}\n现价: {final_price}\n折扣: {discount_percentage}%'
    else:
        ret += f'\n价格: {final_price}'

    ret += f'\n链接: https://store.steampowered.com/app/{appid}'
    return ret


async def _send_steam_message(appinfo: dict, bot: Bot, event: Event):
    header_img = appinfo['header_image']
    bg_img = appinfo['background_raw']
    text_msg = _generate_message(appinfo)

    msg = unified.Message()
    msg.append(unified.MessageSegment.image(header_img, '头图'))
    msg.append(unified.MessageSegment.text(text_msg))
    msg.append(unified.MessageSegment.image(bg_img, '背景图'))
    await msg.send(bot, event)


_steam_command_handler = on_command('steam', aliases={'sbeam', '蒸汽', '蒸汽平台'}, block=True)
@_steam_command_handler.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        if msg.isdigit():
            if appinfo := await fetch_steam_app_info(msg, _steam_config.steam_language, _steam_config.steam_region):
                if appinfo.get(msg, {}).get('success', False):
                    appinfo = appinfo[msg]['data']
                    await _send_steam_message(appinfo, bot, event)
                    await _steam_command_handler.finish()
                else:
                    await _steam_command_handler.finish('未找到该游戏')
            else:
                await _steam_command_handler.finish('请求失败')
        else:
            await _steam_command_handler.finish('请输入正确的游戏ID')


_steam_link_handler = on_regex(r'(?:https?:\/\/)?store\.steampowered\.com\/app\/(\d+)', block=True)
@_steam_link_handler.handle()
async def _(bot: Bot, event: Event, state: T_State):
    appid = state['_matched_groups'][0]
    if appinfo := await fetch_steam_app_info(appid, _steam_config.steam_language, _steam_config.steam_region):
        if appinfo.get(appid, {}).get('success', False):
            appinfo = appinfo[appid]['data']
            await _send_steam_message(appinfo, bot, event)
            await _steam_link_handler.finish()
