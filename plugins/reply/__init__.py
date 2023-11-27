from nonebot import on_command, on_regex
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

import essentials.libraries.user
from essentials.libraries import util

from . import reply

__plugin_meta__ = PluginMetadata(
    name='自动回复',
    description='自动回复，附赠自动水群功能',
    usage=f'/<reply|回复|说话|回答我> <要说的话>，或者也有几率触发机器人自动回复'
)

_reply_handler = on_command('reply', aliases={'回复', '说话', '回答我'}, block=True)
_auto_reply_handler = on_regex(r'.*', rule=reply.check_reply, block=True, priority=100)


@_reply_handler.handle()
async def _(event: Event, bot: Bot, args: Message = CommandArg()):
    my_name = await util.get_bot_name(event, bot, reply.BOT_NAME)
    user_name = await essentials.libraries.user.get_user_name(event, bot, reply.SENDER_NAME)
    if msg := args.extract_plain_text():
        if msg.startswith('_'):
            gid = util.get_group_id(event)
            if msg.lower() == '_enable':
                reply.set_auto_reply_enable(gid, True)
                await _reply_handler.finish('已启用自动回复')
            elif msg.lower() == '_disable':
                reply.set_auto_reply_enable(gid, False)
                await _reply_handler.finish('已禁用自动回复')
            elif msg.lower().startswith('_rate'):
                splitted = msg.split()
                if len(splitted) == 1:
                    await _reply_handler.finish(f'当前自动回复概率为{reply.get_reply_rate(gid) * 100}%')
                else:
                    rate = float(msg.split()[1])
                    if 0 <= rate <= 1:
                        reply.set_reply_rate(gid, rate)
                        await _reply_handler.finish(f'已将自动回复概率设置为{rate * 100}%')
                    else:
                        await _reply_handler.finish('概率必须在0~1之间')
        resp = reply.generate_response(msg).format(me=my_name, name=user_name, segment='\n')
        for i in resp.split('\n'):
            await _reply_handler.send(i)
        await _reply_handler.finish()
    await _reply_handler.finish(reply.UNKNOWN_RESPONSE.format(me=my_name, name=user_name, segment='\n'))


@_auto_reply_handler.handle()
async def _(event: Event, bot: Bot):
    my_name = await util.get_bot_name(event, bot, reply.BOT_NAME)
    user_name = await essentials.libraries.user.get_user_name(event, bot, reply.SENDER_NAME)
    if msg := event.get_plaintext():
        resp = reply.generate_response(msg, False).format(me=my_name, name=user_name)
        if resp:
            for i in resp.split('\n'):
                await _reply_handler.send(i)
    await _reply_handler.finish()
