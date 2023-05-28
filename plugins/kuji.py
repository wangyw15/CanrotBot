from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata

from ..libraries import user, economy, universal_adapters, kuji
from ..libraries.assets import get_assets

__plugin_meta__ = PluginMetadata(
    name='浅草寺',
    description='赛博浅草寺',
    usage='/<kuji|浅草寺>',
    config=None
)

kuji_data: list[str] = [x[1] for x in get_assets('kuji')]

# message
_kuji_handler = on_command('kuji', aliases={'浅草寺'}, block=True)
@_kuji_handler.handle()
async def _(bot: Bot, event: Event):
    if not economy.pay(user.get_uid(universal_adapters.get_puid(bot, event)), 10):
        await _kuji_handler.finish('你的余额不足哦')

    msg = '谢谢你的十个胡萝卜片喵~\n'
    if universal_adapters.is_onebot_v11(bot):
        result = await kuji.generate_kuji()
        msg += f'[CQ:image,file=base64://{result[0]}]'
        await _kuji_handler.finish(universal_adapters.ob11.Message(msg))
    elif universal_adapters.is_onebot_v12(bot):
        result = await kuji.generate_kuji()
        msg += f'[CQ:image,file=base64://{result[0]}]'
        await _kuji_handler.finish(universal_adapters.ob12.Message(msg))
    else:
        result = await kuji.generate_kuji(None)
        msg += kuji.generate_kuji_str(result[1])
        await _kuji_handler.finish(msg)
