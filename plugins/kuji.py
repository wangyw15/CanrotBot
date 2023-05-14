from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata
import random

from ..libraries.assets import get_assets
from ..libraries import user, economy, universal_adapters

__plugin_meta__ = PluginMetadata(
    name='浅草寺',
    description='赛博浅草寺',
    usage='/<kuji|浅草寺>',
    config=None
)

kuji_data: list[str] = [x[1] for x in get_assets('kuji')]

# message
kuji = on_command('kuji', aliases={'浅草寺'}, block=True)
@kuji.handle()
async def _(bot: Bot, event: Event):
    if not economy.pay(user.get_uid(universal_adapters.get_puid(bot, event)), 1):
        await kuji.finish('你的余额不足哦')
    await kuji.finish('谢谢你的一个胡萝卜片喵~\n' + random.choice(kuji_data))
