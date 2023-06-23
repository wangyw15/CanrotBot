from nonebot import on_regex
from nonebot.params import T_State

from . import dice


_dice_handler = on_regex(r'((\d+)?d(\d+)|\d+)(\+((\d+)?d(\d+)|\d+))*', block=True)
@_dice_handler.handler()
async def _(state: T_State):
    await _dice_handler.finish(str(dice.dice_command(state['_matched_str'])))
