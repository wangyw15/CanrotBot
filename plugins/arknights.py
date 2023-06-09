import json
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
    if len(args) == 0:
        await _arknights_handler.finish('用法: ' + __plugin_meta__.usage +
                                        '\n命令列表:\n十连, gacha: 一发十连！')

    uid = user.get_uid(user.get_puid(bot, event))
    if args[0] in ['gacha', '十连', '抽卡']:
        # 付钱
        if not economy.pay(uid, 25):
            await _arknights_handler.finish('你的余额不足喵~')

        # 获取历史寻访结果
        gacha_result_str = user.get_data_by_uid(uid, 'arknights_gacha_result')
        if gacha_result_str == '':
            # 未抽过卡
            # 遵守原版数据格式，rarity为星级-1
            gacha_result = {'5': 0, '4': 0, '3': 0, '2': 0, 'times': 0, 'last_5': 0}
        else:
            gacha_result = json.loads(gacha_result_str)

        # 抽卡
        img, operators = await arknights.generate_gacha(gacha_result['last_5'])

        # 统计本次寻访结果
        # 是否抽到六星
        got_ssr = False
        # 抽卡次数+10
        gacha_result['times'] += 10
        # 统计寻访结果
        for operator in operators:
            if operator['rarity'] == 5:
                got_ssr = True
            gacha_result[str(operator['rarity'])] += 1
        # 上次抽到六星
        if got_ssr:
            gacha_result['last_5'] = 0
        else:
            gacha_result['last_5'] += 10
        # 保存寻访结果
        user.set_data_by_uid(uid, 'arknights_gacha_result',
                             json.dumps(gacha_result, ensure_ascii=False).replace('"', '""'))

        # 发送消息
        msg = unified.Message()
        # 付款提示
        msg.append('你的二十五个胡萝卜片我就收下了喵~\n')
        # 列出抽到的干员
        operator_msg = ''
        for operator in operators:
            operator_msg += f"{operator['rarity'] + 1}星 {operator['name']}\n"
        msg.append('明日方舟抽卡结果: \n' + operator_msg)
        # 统计寻访结果
        msg.append(f"历史抽卡结果: {gacha_result['5']}个六星, "
                   f"{gacha_result['4']}个五星, "
                   f"{gacha_result['3']}个四星, "
                   f"{gacha_result['2']}个三星\n")
        # 是否抽到六星
        if got_ssr:
            msg.append(f"恭喜你抽到六星了喵！距离上次六星已经{gacha_result['last_5']}抽了喵~")
        else:
            msg.append(f"距离上次六星已经{gacha_result['last_5']}次十连了喵~")
        msg.append(unified.MessageSegment.image(img, '十连结果'))
        await msg.send(bot, event)
        await _arknights_handler.finish()

    if args[0] in ['gachainfo', '抽卡记录', '抽卡统计', '抽卡历史', '十连历史', '十连统计', '寻访历史', '寻访统计']:
        gacha_result_str = user.get_data_by_uid(uid, 'arknights_gacha_result')
        if gacha_result_str == '':
            # 未抽过卡
            await _arknights_handler.finish('你还没有抽过卡喵~')
        else:
            gacha_result = json.loads(gacha_result_str)
            msg = '明日方舟抽卡统计: \n' \
                  f"寻访次数: {gacha_result['times']}\n" \
                  f"消耗合成玉: {gacha_result['times'] * 600}\n" \
                  f"= 至纯源石: {round(gacha_result['times'] * 600 / 180, 2)}\n" \
                  f"= RMB: {round(gacha_result['times'] * 600 / 180 * 6, 2)}\n" \
                  f"3星干员: {gacha_result['2']}\n" \
                  f"4星干员: {gacha_result['3']}\n" \
                  f"5星干员: {gacha_result['4']}\n" \
                  f"6星干员: {gacha_result['5']}\n" \
                  f"距离上次抽到6星次数: {gacha_result['last_5']}"
            await _arknights_handler.finish(msg)
