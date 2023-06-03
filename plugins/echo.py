from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='复读机',
    description='复读你发的话',
    usage='/<echo|复读|复读机|回声> [要发出来的消息]',
    config=None
)

_echo_handler = on_command('echo', aliases={'复读', '复读机', '回声'}, block=True)
@_echo_handler.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        await _echo_handler.finish(msg)
    await _echo_handler.finish('111')
