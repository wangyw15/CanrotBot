from typing import Annotated
from datetime import datetime

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment, Bot, Event
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from ..adapters import unified
from ..libraries import mltd


__plugin_meta__ = PluginMetadata(
    name='MLTD',
    description='偶像大师-百万现场剧场时光有关的功能',
    usage='/<mltd> <功能还不知道有什么>',
    config=None
)

event_type = ['Showtime',
              'Millicolle!',
              'Theater',
              'Tour',
              'Anniversary',
              'Working',
              'April Fool',
              'Game Corner',
              'Millicolle! (Box Gasha)',
              'Twin Stage (High Score by Song)',
              'Tune',
              'Twin Stage (Total High Score)',
              'Tale / Time',
              'Talk Party',
              'Treasure']

appeal_type = ['None', 'Vocal', 'Dance', 'Visual']


def iso8601_to_local(iso8601: str) -> str:
    return datetime.fromisoformat(iso8601).astimezone().strftime('%Y年%m月%d日 %H:%M:%S')


_mltd_handler = on_shell_command('mltd', aliases={'百万现场'}, block=True)
@_mltd_handler.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if args[0] in ['活动', 'event', 'events']:
        data = await mltd.get_events()
        if data:
            msg = unified.Message('现在正在进行的活动:\n\n')
            for mltd_event in data:
                # 活动信息
                text_msg = f"{mltd_event['name']}\n" \
                           f"类型: {event_type[mltd_event['type'] - 1]}\n" \
                           f"Appeal 类型: {appeal_type[mltd_event['appealType']]}\n" \
                           f"活动开始时间: {iso8601_to_local(mltd_event['schedule']['beginAt'])}\n" \
                           f"活动结束时间: {iso8601_to_local(mltd_event['schedule']['endAt'])}\n" \
                           f"页面开放时间: {iso8601_to_local(mltd_event['schedule']['pageOpenedAt'])}\n" \
                           f"页面关闭时间: {iso8601_to_local(mltd_event['schedule']['pageClosedAt'])}\n"
                text_msg += f"加速开始时间: {iso8601_to_local(mltd_event['schedule']['boostBeginAt'])}\n" \
                            if mltd_event['schedule']['boostBeginAt'] else ''
                text_msg += f"加速结束时间: {iso8601_to_local(mltd_event['schedule']['boostEndAt'])}\n" \
                            if mltd_event['schedule']['boostEndAt'] else ''
                text_msg += f"活动物品: {mltd_event['item']['name']}" if mltd_event['item']['name'] else ''
                text_msg += '\n\n'
                # 活动封面
                img_url = f"https://storage.matsurihi.me/mltd/event_bg/{str(mltd_event['id']).zfill(4)}.png"
                # 构建信息
                msg.append(unified.MessageSegment.image(img_url, mltd_event['name'] + ' 封面图'))
                msg.append(text_msg)
            await msg.send(bot, event)
            await _mltd_handler.finish()
        else:
            await _mltd_handler.finish('现在还没有活动喵~')
