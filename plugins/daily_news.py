from nonebot import get_driver, on_command
from nonebot.adapters import Bot
from nonebot.plugin import PluginMetadata

from ..universal_adapters import get_image_message_from_url
from ..data import add_help_message

add_help_message('daily', '每日新闻')

img_url = 'https://api.03c3.cn/zb/'

daily = on_command('daily', aliases={'每日新闻'}, block=True)
@daily.handle()
async def _(bot: Bot):
    await daily.finish(await get_image_message_from_url(bot, img_url))
