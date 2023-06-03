from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='计算器',
    description='简单的计算器',
    usage='输入表达式，以等号结尾，比如：1+1=',
    config=None
)

_echo_handler = on_command('echo', aliases={'复读', '复读机', '回声'}, block=True)
@_echo_handler.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        await _echo_handler.finish(msg)
    await _echo_handler.finish('111')
