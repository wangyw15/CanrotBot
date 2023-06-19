from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata

from ..adapters import unified
from ..libraries import kuji
from ..essentials.libraries import user, economy

__plugin_meta__ = PluginMetadata(
    name='浅草寺',
    description='赛博浅草寺',
    usage='/<kuji|浅草寺>',
    config=None
)

# message
_kuji_handler = on_command('kuji', aliases={'浅草寺'}, block=True)
@_kuji_handler.handle()
async def _(bot: Bot, event: Event):
    if not economy.pay(user.get_uid(user.get_puid(bot, event)), 10):
        await _kuji_handler.finish('你的余额不足哦')

    msg = unified.Message()
    msg.append('谢谢你的十个胡萝卜片喵~\n')
    result = await kuji.generate_kuji()
    msg.append(unified.MessageSegment.image(result[0], result[1]))
    await msg.send(bot, event)
    await _kuji_handler.finish()
