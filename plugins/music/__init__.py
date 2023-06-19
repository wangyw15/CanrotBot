import re
from typing import Literal

from nonebot import on_regex, on_command
from nonebot.adapters import Bot, Event, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from . import music
from ...adapters import unified

__plugin_meta__ = PluginMetadata(
    name='音乐插件',
    description='解析音乐分享链接的内容转为音乐卡片，还有点歌功能',
    usage='/点歌 关键词\n/网易点歌 关键词',
    config=None
)

_qqmusic_id_pattern = r'(?:https?:\/\/)?(?:\S+\.)?y\.qq\.com\/\S+(?:songid=|songDetail\/)(\d+)'


async def _send_music_card(bot: Bot, event: Event, music_type: Literal['qq', '163'], music_id: str | int):
    if unified.Detector.is_onebot_v11(bot):
        await bot.send(event, unified.adapters.onebot_v11.Message(f'[CQ:music,type={music_type},id={music_id}]'))
    elif unified.Detector.is_onebot_v12(bot):
        await bot.send(event, unified.adapters.onebot_v12.Message(f'[CQ:music,type={music_type},id={music_id}]'))


_cloudmusic_handler = on_regex(r'(?:https?:\/\/)?(?:y\.)?music\.163\.com\/(?:\S+\/)?song\?\S*id=(\d+)', block=True)
@_cloudmusic_handler.handle()
async def _(state: T_State, bot: Bot, event: Event):
    music_id = state['_matched_groups'][0]
    if unified.Detector.is_onebot(bot):
        await _send_music_card(bot, event, '163', music_id)
    await _cloudmusic_handler.finish()


_qqmusic_link_handler = on_regex(_qqmusic_id_pattern, block=True)
@_qqmusic_link_handler.handle()
async def _(state: T_State, bot: Bot, event: Event):
    music_id = state['_matched_groups'][0]
    if unified.Detector.is_onebot(bot):
        await _send_music_card(bot, event, 'qq', music_id)
    await _qqmusic_link_handler.finish()


_qqmusic_shortlink_handler = on_regex(r'(?:https?:\/\/)?c6\.y\.qq\.com\/base\/fcgi-bin\/u\?__=(\w+)', block=True)
@_qqmusic_shortlink_handler.handle()
async def _(state: T_State, bot: Bot, event: Event):
    link = state['_matched_str']
    resolved = await music.resolve_shortlink(link)
    if resolved:
        music_id = re.search(_qqmusic_id_pattern, resolved).groups()[0]
        if unified.Detector.is_onebot(bot):
            await _send_music_card(bot, event, 'qq', music_id)
        await _qqmusic_shortlink_handler.finish()


_qq_music_handler = on_command('点歌', block=True)
@_qq_music_handler.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if not unified.Detector.is_onebot(bot):
        await _qq_music_handler.finish('只有 OneBot 协议才支持点歌')

    if keyword := args.extract_plain_text():
        search_result = await music.search_qq_music(keyword)
        if search_result:
            music_id = search_result[0]['id']
            if unified.Detector.is_onebot(bot):
                await _send_music_card(bot, event, 'qq', music_id)
                await _qq_music_handler.finish()
    else:
        await _qq_music_handler.finish('请输入歌曲名')


_netease_music_handler = on_command('网易点歌', block=True)
@_netease_music_handler.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if not unified.Detector.is_onebot(bot):
        await _netease_music_handler.finish('只有 OneBot 协议才支持点歌')

    if keyword := args.extract_plain_text():
        search_result = await music.search_netease_music(keyword)
        if search_result:
            music_id = search_result[0]['id']
            if unified.Detector.is_onebot(bot):
                await _send_music_card(bot, event, '163', music_id)
                await _netease_music_handler.finish()
    else:
        await _netease_music_handler.finish('请输入歌曲名')
