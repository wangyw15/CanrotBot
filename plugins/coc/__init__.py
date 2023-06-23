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
        if re.match(r'((\d+)?[Dd](\d+)|\d+)(\+((\d+)?[Dd](\d+)|\d+))*', args[0]):
            await _dice_handler.finish(args[0] + ' = ' + str(dice.dice_command(args[0])))
        else:
            await _dice_handler.finish('骰子指令格式错误')
