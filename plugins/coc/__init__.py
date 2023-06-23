import re
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from . import dice

__plugin_meta__ = PluginMetadata(
    name='跑团工具',
    description='只做了骰子',
    usage='/<dice|d|骰子> <骰子指令>',
    config=None
)


_dice_handler = on_shell_command('dice', aliases={'骰子', 'd'}, block=True)
@_dice_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1:
        result = dice.dice_expression(args[0])
        await _dice_handler.finish(args[0] + ' = ' + result[1] + ' = ' + str(result[0]))
