from typing import Annotated
from datetime import datetime

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from ..adapters import unified


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
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if args[0] in ['活动', 'event']:
        data = await unified.util.fetch_json_data('https://api.matsurihi.me/api/mltd/v2/events?at=now')
        if data:
            msg = ''
            for event in data:
                msg += f"活动名称: {event['name']}" \
                       f"活动类型: {event_type[event['type'] - 1]}" \
                       f"Appeal 类型: {appeal_type[event['appealType']]}" \
                       f"活动开始时间: {iso8601_to_local(event['schedule']['beginAt'])}" \
                       f"活动结束时间: {iso8601_to_local(event['schedule']['endAt'])}" \
                       f"活动页面开放时间: {iso8601_to_local(event['schedule']['pageOpenedAt'])}" \
                       f"活动页面关闭时间: {iso8601_to_local(event['schedule']['pageClosedAt'])}" \
                       f"活动加速开始时间: {iso8601_to_local(event['schedule']['boostBeginAt'])}" \
                       f"活动加速结束时间: {iso8601_to_local(event['schedule']['boostEndAt'])}" \
                       f"活动物品: {event['item']['name']}" if event['item']['name'] else '' \
                       '\n'
            await _mltd_handler.finish(msg)
        else:
            await _mltd_handler.finish('现在还没有活动喵~')
