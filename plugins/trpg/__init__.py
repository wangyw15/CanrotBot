import typing

from nonebot import on_command, on_shell_command
from nonebot.adapters import Message, MessageSegment
from nonebot.params import CommandArg, ShellCommandArgv
from nonebot.plugin import PluginMetadata

from . import dice, investigator

__plugin_meta__ = PluginMetadata(
    name='跑团工具',
    description='只做了骰子',
    usage='/<dice|d|骰子> <骰子指令>',
    config=None
)


_dice_handler = on_command('dice', aliases={'骰子', 'd'}, block=True)
@_dice_handler.handle()
async def _(args: Message = CommandArg()):
    if expr := args.extract_plain_text():
        result, calculated_expr = dice.dice_expression(expr)
        if str(result) == calculated_expr:
            await _dice_handler.finish(expr + ' = ' + str(result))
        else:
            await _dice_handler.finish(expr + ' = ' + calculated_expr + ' = ' + str(result))


_card_handler = on_shell_command('card', aliases={'c', '调查员', '人物卡'}, block=True)
@_card_handler.handle()
async def _(args: typing.Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1 and args[0].lower() in ['r', 'random', '随机', '随机生成']:
        card = investigator.random_basic_properties()
        msg = ''
        for k, v in card.items():
            msg += f'{k}: {v}\n'
        await _card_handler.finish(msg.strip())
    await _card_handler.finish(__plugin_meta__.usage)
