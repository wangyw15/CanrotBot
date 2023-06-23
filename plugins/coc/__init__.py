from nonebot import on_regex
from nonebot.params import T_State

from . import dice


_dice_handler = on_regex(r'((\d+)?d(\d+)|\d+)(\+((\d+)?d(\d+)|\d+))*', block=True)
@_dice_handler.handle()
async def _(state: T_State):
    command = state['_matched_str']
    await _dice_handler.finish(command + ' = ' + str(dice.dice_command(command)))
