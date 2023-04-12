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
    steam_proxy: str = ''

    @validator('steam_enabled')
    def steam_enabled_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('steam_enabled must be a bool')
        return v
    
    @validator('steam_proxy')
    def steam_proxy_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('steam_proxy must be a str')
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
    resp = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={appid}&l=zh-cn&cc=cn', 
                        proxies={'https': config.steam_proxy, 'http': config.steam_proxy},
                        headers={'Accept-Language': 'zh-cn'})
    if resp.ok and resp.status_code == 200:
        return resp.json()
    return None

def fetch_data(url: str) -> bytes | None:
    resp = requests.get(url)
    if resp.ok and resp.status_code == 200:
        return resp.content
    return None

def generate_message(app_info: dict) -> str:
    name: str = app_info['name']
    appid: int = app_info['steam_appid']
    desc: str = app_info['short_description']
    developers: list[str] = app_info['developers']
    publishers: list[str] = app_info['publishers']
    initial_price: str = app_info['price_overview']['initial_formatted']
    final_price:str = app_info['price_overview']['final_formatted']
    discount_percentage: int = app_info['price_overview']['discount_percent']

    ret = f"""
名称: {name}
开发商: {', '.join(developers)}
发行商: {', '.join(publishers)}
简介: {desc}
    """.strip()

    if discount_percentage != 0:
        ret += f'\n原价: {initial_price}\n现价: {final_price}\n折扣: {discount_percentage}%'
    else:
        ret += f'\n价格: {final_price}'

    ret += f'\n链接: https://store.steampowered.com/app/{appid}'
    return ret

steam = on_command('steam', aliases={'蒸汽', '蒸汽平台'}, rule=is_enabled, block=True)
@steam.handle()
async def _(bot: Bot, args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        if msg.isdigit():
            if appinfo := fetch_app_info(msg):
                if appinfo.get(msg, {}).get('success', False):
                    appinfo = appinfo[msg]['data']
                    text_msg = generate_message(appinfo)
                    img = appinfo['header_image']
                    if ob11 and isinstance(bot, ob11.Bot):
                        await steam.finish(ob11.MessageSegment.image(img) + '\n' + text_msg)
                    elif ob12 and isinstance(bot, ob12.Bot):
                        await steam.finish(ob12.MessageSegment.image(img) + '\n' + text_msg)
                    elif mirai2 and isinstance(bot, mirai2.Bot):
                        await steam.finish(mirai2.MessageSegment.image(img) + '\n' + text_msg)
                    else:
                        await steam.finish(text_msg)
                else:
                    await steam.finish('未找到该游戏')
            else:
                await steam.finish('请求失败')
        else:
            await steam.finish('请输入正确的游戏ID')
