import typing

from nonebot import on_command, on_shell_command
from nonebot.adapters import Message, MessageSegment, Bot, Event
from nonebot.params import CommandArg, ShellCommandArgv
from nonebot.plugin import PluginMetadata

from essentials.libraries import user
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
async def _(bot: Bot, event: Event, args: typing.Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    puid = user.get_puid(bot, event)
    uid = user.get_uid(puid)
    if not uid:
        await _card_handler.finish('还未注册或绑定账号')
    if len(args) == 1:
        if args[0].lower() in ['r', 'random', '随机', '随机生成']:
            card = investigator.random_basic_properties()
            await _card_handler.finish('&'.join([f'{k}={v}' for k, v in card.items()]))
        elif args[0].lower() in ['l', 'list', '卡片列表']:
            cards = investigator.get_card(uid)
            if cards:
                final_msg = '调查员列表:\n\n'
                for cid, card in cards.items():
                    final_msg += f'调查员卡片 id: {cid}\n'
                    final_msg += '\n'.join([f'{k}={v}' for k, v in card.items()])
                    final_msg += '\n\n'
                await _card_handler.finish(final_msg.strip())
            else:
                await _card_handler.finish('还未导入人物卡')
    elif len(args) == 2 and args[0].lower() in ['d', 'delete', '删除', '移除']:
        cid = args[1]
        if investigator.delete_card(uid, cid):
            await _card_handler.finish(f'调查员 {cid} 删除成功')
        else:
            await _card_handler.finish(f'删除失败')
    elif len(args) > 0 and args[0].lower() in ['a', 'add', '导入', '添加']:
        cid = investigator.set_card(uid, investigator.generate_card(' '.join(args[1:])))
        await _card_handler.finish(f'添加成功，人物卡 id 为 {cid}')
    await _card_handler.finish(__plugin_meta__.usage)
