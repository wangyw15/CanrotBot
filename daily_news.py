from nonebot import get_driver, on_command
from nonebot.adapters import Bot
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel, validator

from .universal_adapters import get_image_message_from_url

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

daily = on_command('daily', aliases={'每日新闻'}, rule=is_enabled, block=True)
@daily.handle()
async def _(bot: Bot):
    await daily.finish(await get_image_message_from_url(bot, img_url))
