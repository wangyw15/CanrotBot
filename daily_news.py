from nonebot import get_driver, on_command
from nonebot.adapters import Bot
from nonebot.plugin import PluginMetadata
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
    import nonebot.adapters.kaiheila as kook
except:
    kook = None
try:
    import nonebot.adapters.mirai2 as mirai2
except:
    mirai2 = None

# config
class DailyNewsConfig(BaseModel):
    daily_news_enabled: bool = True

    @validator('daily_news_enabled')
    def daily_news_enabled_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('daily_news_enabled must be a bool')
        return v

# metadata
__plugin_meta__ = PluginMetadata(
    name='Daily News',
    description='每日新闻',
    usage='/daily',
    config=DailyNewsConfig,
)
config = DailyNewsConfig.parse_obj(get_driver().config)

# enabled
async def is_enabled() -> bool:
    return config.daily_news_enabled

img_url = 'https://api.03c3.cn/zb/'

def fetch_daily_image() -> bytes | None:
    resp = requests.get(img_url)
    if resp.ok and resp.status_code == 200:
        return resp.content
    return None

daily = on_command('daily', aliases={'每日新闻'}, rule=is_enabled, block=True)
@daily.handle()
async def _(bot: Bot):
    if ob11 and isinstance(bot, ob11.Bot):
        await daily.finish(ob11.MessageSegment.image(file = img_url))
    elif ob12 and isinstance(bot, ob12.Bot):
        await daily.finish(ob12.MessageSegment.image(file = img_url))
    elif kook and isinstance(bot, kook.Bot):
        img_data = fetch_daily_image()
        if img_data:
            url = await bot.upload_file(img_data)
            await daily.finish(kook.MessageSegment.image(url))
    elif mirai2 and isinstance(bot, mirai2.Bot):
        await daily.finish(mirai2.MessageSegment.image(url = img_url))
