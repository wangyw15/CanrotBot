from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from pydantic import BaseModel, validator
import requests

# different bots
try:
    import nonebot.adapters.onebot.v11 as ob11
except:
    ob11 = None
try:
    import nonebot.adapters.onebot.v12 as ob12
except:
    ob12 = None
try:
    import nonebot.adapters.mirai2 as mirai2
except:
    mirai2 = None

# config
class SteamConfig(BaseModel):
    steam_enabled: bool = True

    @validator('steam_enabled')
    def steam_enabled_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('steam_enabled must be a bool')
        return v

# metadata
__plugin_meta__ = PluginMetadata(
    name='Steam',
    description='Steam相关功能',
    usage='/steam',
    config=SteamConfig,
)

config = SteamConfig.parse_obj(get_driver().config)

# plugin enabled
async def is_enabled() -> bool:
    return config.steam_enabled

# fetch app info from appid
def fetch_app_info(appid: int) -> dict | None:
    resp = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={appid}&l=zh-cn')
    if resp.ok and resp.status_code == 200:
        return resp.json()
    return None

def fetch_data(url: str) -> bytes | None:
    resp = requests.get(url)
    if resp.ok and resp.status_code == 200:
        return resp.content
    return None

steam = on_command('steam', aliases={'蒸汽', '蒸汽平台'}, rule=is_enabled, block=True)
@steam.handle()
async def _(bot: Bot, args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        if msg.isdigit():
            if appinfo := fetch_app_info(msg):
                if appinfo.get(msg, {}).get('success', False):
                    appinfo = appinfo[msg]['data']
                    name = appinfo['name']
                    desc = appinfo['short_description']
                    img = appinfo['header_image']
                    price = appinfo['price_overview']['initial_formatted']
                    discounted = appinfo['price_overview']['final_formatted']
                    discount_percentage = appinfo['price_overview']['discount_percent']
                    if ob11 and isinstance(bot, ob11.Bot):
                        resp_msg = ob11.MessageSegment.image(img) + f'\n名称: {name}\n简介: {desc}'
                        if discount_percentage != 0:
                            resp_msg += f'\n原价: {price}\n现价: {discounted}\n折扣: {discount_percentage}%'
                        else:
                            resp_msg += f'\n价格: {price}'
                        resp_msg += f'\n链接: https://store.steampowered.com/app/{msg}'
                        await steam.finish(resp_msg)
                    elif ob12 and isinstance(bot, ob12.Bot):
                        resp_msg = ob12.MessageSegment.image(img) + f'\n名称: {name}\n简介: {desc}'
                        if discount_percentage != 0:
                            resp_msg += f'\n原价: {price}\n现价: {discounted}\n折扣: {discount_percentage}%'
                        else:
                            resp_msg += f'\n价格: {price}'
                        resp_msg += f'\n链接: https://store.steampowered.com/app/{msg}'
                        await steam.finish(resp_msg)
                    elif mirai2 and isinstance(bot, mirai2.Bot):
                        resp_msg = ob12.MessageSegment.image(img) + f'\n名称: {name}\n简介: {desc}'
                        if discount_percentage != 0:
                            resp_msg += f'\n原价: {price}\n现价: {discounted}\n折扣: {discount_percentage}%'
                        else:
                            resp_msg += f'\n价格: {price}'
                        resp_msg += f'\n链接: https://store.steampowered.com/app/{msg}'
                        await steam.finish(resp_msg)
                    else:
                        resp_msg = f'名称: {name}\n简介: {desc}'
                        if discount_percentage != 0:
                            resp_msg += f'\n原价: {price}\n现价: {discounted}\n折扣: {discount_percentage}%'
                        else:
                            resp_msg += f'\n价格: {price}'
                        resp_msg += f'\n链接: https://store.steampowered.com/app/{msg}'
                        await steam.finish(resp_msg)
                else:
                    await steam.finish('未找到该游戏')
            else:
                await steam.finish('请求失败')
        else:
            await steam.finish('请输入正确的游戏ID')
