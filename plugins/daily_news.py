from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata

from ..libraries.universal_adapters import send_image

__plugin_meta__ = PluginMetadata(
    name='看新闻',
    description='每日新闻',
    usage='/<daily|新闻|每日新闻>',
    config=None
)


daily = on_command('daily', aliases={'每日新闻', '新闻'}, block=True)
@daily.handle()
async def _(bot: Bot, event: Event):
    await send_image('https://api.03c3.cn/zb/', bot, event)
    await daily.finish()
