from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment, Bot, Event
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from ..libraries import arknights, economy, user
from ..adapters import unified

__plugin_meta__ = PluginMetadata(
    name='明日方舟助手',
    description='现在只做了抽卡，未来会加的（画饼',
    usage='/<arknights|粥|舟|方舟|明日方舟> <命令>',
    config=None
)

_arknights_handler = on_shell_command('arknights', aliases={'粥', '舟', '方舟', '明日方舟'}, block=True)
@_arknights_handler.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1:
        await _arknights_handler.finish('用法: ' + __plugin_meta__.usage +
                                        '\n命令列表:\n十连, gacha: 一发十连！')
    if args[0] in ['十连', 'gacha']:
        if not economy.pay(user.get_uid(unified.get_puid(bot, event)), 25):
            await _arknights_handler.finish('你的余额不足喵~')

        img, operators = await arknights.generate_gacha()
        msg = unified.Message()
        operator_msg = ''
        for operator in operators:
            operator_msg += f"{operator['rarity'] + 1}星 {operator['name']}\n"
        msg.append('抽到了: \n' + operator_msg)
        msg.append(unified.MessageSegment.image(img, '十连结果'))
        await msg.send(bot, event)
        await _arknights_handler.finish()
