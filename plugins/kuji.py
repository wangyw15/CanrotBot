import base64

from nonebot import on_command
from nonebot.adapters import Bot, Event, Message, MessageSegment
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
    if universal_adapters.can_send_image(bot):
        result = await kuji.generate_kuji()
        final_msg = Message()
        final_msg.append(msg)
        final_msg.append(MessageSegment(type='image', data={'bytes': result[0]}))
        await universal_adapters.send_rich_text_message(final_msg, bot, event)
    # if universal_adapters.is_onebot_v11(bot):
    #     result = await kuji.generate_kuji()
    #     msg = msg + universal_adapters.ob11.MessageSegment.image(result[0])
    #     await _kuji_handler.finish(msg)
    # elif universal_adapters.is_onebot_v12(bot):
    #     result = await kuji.generate_kuji()
    #     b64img = base64.b64encode(result[0]).decode('utf-8')
    #     msg += f'[CQ:image,file=base64://{b64img}]'
    #     await _kuji_handler.finish(universal_adapters.ob12.Message(msg))
    # elif universal_adapters.is_kook(bot):
    #     result = await kuji.generate_kuji()
    #     await _kuji_handler.send(msg.strip())
    #     await universal_adapters.send_image(result[0], bot, event)
    #     await _kuji_handler.finish()
    # elif universal_adapters.is_qqguild(bot):
    #     result = await kuji.generate_kuji()
    #     msg += universal_adapters.qqguild.MessageSegment.file_image(result[0])
    #     await _kuji_handler.finish(msg)
    else:
        result = await kuji.generate_kuji(None)
        msg += kuji.generate_kuji_str(result[1])
        await _kuji_handler.finish(msg)
