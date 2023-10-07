from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment, Bot, Event
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from adapters import unified
from essentials.libraries import user, economy
from . import arknights, data
from storage import database
from sqlalchemy import select

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
        if not economy.pay(uid, 25, '方舟十连'):
            await _arknights_handler.finish('你的余额不足喵~')

        # 抽卡
        img, operators = await arknights.generate_gacha(uid)

        # 付款提示
        await _arknights_handler.send('你的二十五个胡萝卜片我就收下了喵~')
        # 发送消息
        msg = unified.Message()
        # 列出抽到的干员
        operator_msg = ''
        for operator in operators:
            operator_msg += f"{operator['rarity'] + 1}星 {operator['name']}\n"
        msg.append('明日方舟抽卡结果: \n' + operator_msg)
        msg.append(unified.MessageSegment.image(img, '十连结果'))
        await msg.send()
        await _arknights_handler.finish()

    if args[0] in ['gachainfo', '抽卡记录', '抽卡统计', '抽卡历史', '十连历史', '十连统计', '寻访历史', '寻访统计']:
        with database.get_session().begin() as session:
            gacha_result = session.execute(select(data.Statistics).
                                           where(data.Statistics.user_id == uid)).scalar_one_or_none()
            if gacha_result.times == 0:
                # 未抽过卡
                await _arknights_handler.finish('你还没有抽过卡喵~')
            else:
                msg = '明日方舟抽卡统计: \n' \
                      f"寻访次数: {gacha_result.times}\n" \
                      f"消耗合成玉: {gacha_result.times * 600}\n" \
                      f"= 至纯源石: {round(gacha_result.times * 600 / 180, 2)}\n" \
                      f"= RMB: {round(gacha_result.times * 600 / 180 * 6, 2)}\n" \
                      f"3星干员: {gacha_result.three_stars}\n" \
                      f"4星干员: {gacha_result.four_stars}\n" \
                      f"5星干员: {gacha_result.five_stars}\n" \
                      f"6星干员: {gacha_result.six_stars}\n" \
                      f"距离上次抽到6星次数: {gacha_result.last_six_star}"
                await _arknights_handler.finish(msg)
