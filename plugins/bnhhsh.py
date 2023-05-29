from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from ..libraries import bnhhsh

__plugin_meta__ = PluginMetadata(
    name='不能好好说话',
    description='它和「能不能好好说话？」的区别是它不能好好说话，只会说涩涩的话！',
    usage='/<bnhhsh|不能好好说话> <一串英文字母>',
    config=None
)

_bnhhsh_handler = on_shell_command('bnhhsh', aliases={'不能好好说话'}, block=True)
@_bnhhsh_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1:
        await _bnhhsh_handler.finish(bnhhsh.dp(args[0]))
    await _bnhhsh_handler.finish('用法: ' + __plugin_meta__.usage)
