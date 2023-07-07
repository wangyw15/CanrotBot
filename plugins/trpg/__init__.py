import typing

from nonebot import on_command, on_shell_command
from nonebot.adapters import Message, MessageSegment, Bot, Event
from nonebot.params import CommandArg, ShellCommandArgv
from nonebot.plugin import PluginMetadata

from essentials.libraries import user
from . import dice, investigator

__plugin_meta__ = PluginMetadata(
    name='跑团工具',
    description='基本的跑团工具',
    usage='/<dice|d|骰子> <骰子指令>\n'
          '/<investigator|i|调查员|人物卡> <r|l|d|s|a>\n'
          '/<c|check|检定> <属性名称>',
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


_investigator_handler = on_shell_command('investigator', aliases={'i', '调查员', '人物卡'}, block=True)
@_investigator_handler.handle()
async def _(bot: Bot, event: Event, args: typing.Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    puid = user.get_puid(bot, event)
    uid = user.get_uid(puid)
    if not uid:
        await _investigator_handler.finish('还未注册或绑定账号')
    if len(args) == 1:
        if args[0].lower() in ['r', 'random', '随机', '随机生成']:
            card = investigator.random_basic_properties()
            await _investigator_handler.finish('&'.join([f'{k}={v}' for k, v in card.items()]))
        elif args[0].lower() in ['l', 'list', '卡片列表']:
            cards = investigator.get_investigator(uid)
            selected_card = investigator.get_selected_investigator(uid)
            if cards:
                final_msg = '调查员列表: (*表示当前选定的调查员)\n\n'
                for iid, card in cards.items():
                    if selected_card:
                        selected_iid, _ = selected_card.popitem()
                        if iid == selected_iid:
                            final_msg += '*'
                    final_msg += f'调查员 id: {iid}\n'
                    # 基本信息
                    final_msg += f'姓名: {card["name"]}\n'
                    final_msg += f'性别: {card["gender"]}\n'
                    final_msg += f'年龄: {card["age"]}\n'
                    final_msg += f'职业: {card["profession"]}\n'
                    # 基本属性
                    for k, v in card['basic_properties'].items():
                        final_msg += f'{investigator.get_property_name(k)}: {v}\n'
                    # 技能
                    if card['skills']:
                        final_msg += '技能:\n'
                        for k, v in card['skills'].items():
                            final_msg += f'{k}: {v}\n'
                    # 额外属性
                    if card['additional_properties']:
                        final_msg += '额外属性:\n'
                        for k, v in card['additional_properties'].items():
                            final_msg += f'{k}: {v}\n'
                    # 背包
                    if card['items']:
                        final_msg += '背包:\n'
                        for k, v in card['items'].items():
                            final_msg += f'{k}: {v}\n'
                    # 额外信息
                    if card['extra']:
                        final_msg += '额外信息:\n'
                        for k, v in card['extra'].items():
                            final_msg += f'{k}: {v}\n'
                    final_msg += '\n\n'
                await _investigator_handler.finish(final_msg.strip())
            else:
                await _investigator_handler.finish('还未导入人物卡')
    elif len(args) == 2:
        if args[0].lower() in ['d', 'delete', '删除', '移除']:
            iid = args[1]
            if investigator.check_investigator_id(uid, iid):
                card = investigator.get_investigator(uid, iid)
                if investigator.delete_investigator(uid, iid):
                    await _investigator_handler.finish(f'调查员 {card[iid]["name"]}({iid}) 删除成功')
            await _investigator_handler.finish(f'删除失败')
        elif args[0].lower() in ['s', 'select', 'set', '选择', '设置']:
            iid = args[1]
            if investigator.check_investigator_id(uid, iid):
                investigator.set_selected_investigator(uid, iid)
                card = investigator.get_investigator(uid, iid)
                await _investigator_handler.finish(f'已选择调查员 {card[iid]["name"]}({iid})')
    elif len(args) > 0 and args[0].lower() in ['a', 'add', '导入', '添加']:
        card = investigator.generate_investigator(' '.join(args[1:]))
        if not card:
            await _investigator_handler.finish('数据不完整或格式错误')
        else:
            iid = investigator.set_investigator(uid, card)
            await _investigator_handler.finish(f'添加成功，人物卡 id 为 {iid}')
    await _investigator_handler.finish(__plugin_meta__.usage)


_check_handler = on_shell_command('check', aliases={'c', '检定'}, block=True)
@_check_handler.handle()
async def _(bot: Bot, event: Event, args: typing.Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    puid = user.get_puid(bot, event)
    uid = user.get_uid(puid)
    if not uid:
        await _investigator_handler.finish('还未注册或绑定账号')
    if not investigator.get_selected_investigator(uid):
        await _investigator_handler.finish('还未选择调查员')
    iid, card = investigator.get_selected_investigator(uid).popitem()
    if len(args) == 1:
        if args[0] in investigator.basic_property_names:
            target = card['basic_properties'][investigator.get_property_key(args[0])]
            dice_result = dice.simple_dice_expression('d100')
            check_result = '失败'
            if dice_result == 1:
                check_result = '大成功'
            elif dice_result <= target / 5:
                check_result = '极难成功'
            elif dice_result <= target / 2:
                check_result = '困难成功'
            elif dice_result <= target:
                check_result = '成功'
            elif target >= 50 and dice_result == 100 or target < 50 and dice_result >= 96:
                check_result = '大失败'
            await _check_handler.finish(f'调查员 {card["name"]}\n'
                                        f'{args[0]}: {target}\n'
                                        f'd100 = {dice_result}\n'
                                        f'{check_result}')
