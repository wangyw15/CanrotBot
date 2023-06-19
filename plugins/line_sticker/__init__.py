from nonebot import on_regex
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from . import line_sticker
from ...adapters import unified

__plugin_meta__ = PluginMetadata(
    name='Line 表情包下载',
    description='下载 Line 表情包',
    usage='发送链接就可以触发',
    config=None
)


_line_stricker_handler = on_regex(r'(?:https?:\/\/)?store\.line\.me\/stickershop\/product\/(\d+)', block=True)
@_line_stricker_handler.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if not (unified.Detector.is_onebot(bot) or unified.Detector.is_kook(bot)):
        await _line_stricker_handler.finish()
    sticker_id = state['_matched_groups'][0].strip()
    name, content = await line_sticker.get_line_sticker(sticker_id)
    await unified.Message.send_file(content, name + '.zip', bot, event)
    await _line_stricker_handler.finish()
