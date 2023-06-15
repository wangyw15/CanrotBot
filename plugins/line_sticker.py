from nonebot import on_regex
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from httpx import AsyncClient
from tempfile import NamedTemporaryFile
from ..adapters import unified

__plugin_meta__ = PluginMetadata(
    name='Line 表情包下载',
    description='下载 Line 表情包',
    usage='发送链接就可以触发',
    config=None
)

_client = AsyncClient()

_line_stricker_handler = on_regex(r'(?:https?:\/\/)?store\.line\.me\/stickershop\/product\/(\d+)', block=True)
@_line_stricker_handler.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if not unified.Detector.is_onebot(bot):
        await _line_stricker_handler.finish('此平台暂不支持')
    sticker_id = state['_matched_groups'][0].strip()
    with NamedTemporaryFile(suffix='.zip') as f:
        resp = await _client.get(
            f'https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickerpack@2x.zip')
        if resp.is_success and resp.status_code == 200:
            f.write(resp.content)
            f.flush()
        else:
            resp = await _client.get(
                f'https://stickershop.line-scdn.net/stickershop/v1/product/{sticker_id}/iphone/stickers@2x.zip')
            f.write(resp.content)
            f.flush()
        if isinstance(bot, unified.adapters.onebot_v11.Bot) \
                and isinstance(event, unified.adapters.onebot_v11.GroupMessageEvent):
            await bot.call_api('upload_group_file', group_id=event.group_id, file=f.name, name=f'{sticker_id}.zip')
            await _line_stricker_handler.finish()
        if isinstance(bot, unified.adapters.onebot_v12.Bot) \
                and isinstance(event, unified.adapters.onebot_v12.GroupMessageEvent):
            await bot.call_api('upload_group_file', group_id=event.group_id, file=f.name, name=f'{sticker_id}.zip')
            await _line_stricker_handler.finish()
