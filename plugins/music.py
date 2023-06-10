from nonebot import on_regex
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from httpx import AsyncClient
import re

from ..libraries import link_metadata
from ..adapters import unified

__plugin_meta__ = PluginMetadata(
    name='音乐解析',
    description='虽然名字写的音乐解析，但只是解析音乐分享链接的内容',
    usage='发送支持解析的链接会自动触发',
    config=None
)

_qqmusic_id_pattern = r'(?:https?:\/\/)?(?:\S+\.)?y\.qq\.com\/\S+(?:songid=|songDetail\/)(\d+)'
_client = AsyncClient()

_cloudmusic_handler = on_regex(r'(?:https?:\/\/)?(?:y\.)?music\.163\.com\/(\S+\/)?song\?\S*id=(\d+)', block=True)
@_cloudmusic_handler.handle()
async def _(state: T_State, bot: Bot):
    music_id = state['_matched_groups'][0]
    if unified.Detector.is_onebot_v11(bot):
        await _cloudmusic_handler.finish(unified.adapters.onebot_v11.Message(f'[CQ:music,type=163,id={music_id}]'))
    elif unified.Detector.is_onebot_v12(bot):
        await _cloudmusic_handler.finish(unified.adapters.onebot_v12.Message(f'[CQ:music,type=163,id={music_id}]'))
    await _cloudmusic_handler.finish()


_qqmusic_link_handler = on_regex(_qqmusic_id_pattern, block=True)
@_qqmusic_link_handler.handle()
async def _(state: T_State, bot: Bot):
    music_id = state['_matched_groups'][0]
    if unified.Detector.is_onebot_v11(bot):
        await _cloudmusic_handler.finish(unified.adapters.onebot_v11.Message(f'[CQ:music,type=qq,id={music_id}]'))
    elif unified.Detector.is_onebot_v12(bot):
        await _cloudmusic_handler.finish(unified.adapters.onebot_v12.Message(f'[CQ:music,type=qq,id={music_id}]'))
    await _cloudmusic_handler.finish()


_qqmusic_shortlink_handler = on_regex(r'(?:https?:\/\/)?c6\.y\.qq\.com\/base\/fcgi-bin\/u\?__=(\w+)', block=True)
@_qqmusic_shortlink_handler.handle()
async def _(state: T_State, bot: Bot):
    link = state['_matched_str']
    resp = await _client.get(link, follow_redirects=False)
    if resp.is_success and resp.status_code == 302:
        music_id = re.search(_qqmusic_id_pattern, resp.headers['Location']).groups()[0]
        if unified.Detector.is_onebot_v11(bot):
            await _cloudmusic_handler.finish(unified.adapters.onebot_v11.Message(f'[CQ:music,type=qq,id={music_id}]'))
        elif unified.Detector.is_onebot_v12(bot):
            await _cloudmusic_handler.finish(unified.adapters.onebot_v12.Message(f'[CQ:music,type=qq,id={music_id}]'))
        await _cloudmusic_handler.finish()
