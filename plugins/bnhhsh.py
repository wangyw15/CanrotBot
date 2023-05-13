from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message
from nonebot.params import CommandArg

from ..libraries import bnhhsh

__plugin_meta__ = PluginMetadata(
    name='不能好好说话',
    description='它和「能不能好好说话？」的区别是它不能好好说话，只会说涩涩的话！',
    usage='/<bnhhsh|不能好好说话> <一串英文字母>',
    config=None
)

_bnhhsh = on_command('bnhhsh', aliases={'不能好好说话'}, block=True)
@_bnhhsh.handle()
async def _(args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        await _bnhhsh.finish(bnhhsh.dp(msg))
    await _bnhhsh.finish('用法: ' + __plugin_meta__.usage)
