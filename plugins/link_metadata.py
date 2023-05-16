from nonebot import on_regex
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

from ..libraries import link_metadata, universal_adapters

__plugin_meta__ = PluginMetadata(
    name='计算器',
    description='简单的计算器',
    usage='输入表达式，以等号结尾，比如：1+1=',
    config=None
)

def _generate_bilibili_message(data: dict) -> str:
    # either use the first line of description or the first 50 characters of description
    desc = '\n'.join([x.strip() for x in data['desc'].split('\n') if x.strip() != ''])
    if len(desc) > 50:
        desc = desc[:50] + '...'
    # generate message
    msg = f'标题: \n{data["title"]}\nUP主: \n{data["owner"]["name"]}\n播放: {data["stat"]["view"]}\n弹幕: {data["stat"]["danmaku"]}\n点赞: {data["stat"]["like"]}\n投币: {data["stat"]["coin"]}\n简介:\n{data["desc"]}\n视频链接: \nhttps://www.bilibili.com/video/{data["bvid"]}'
    return msg

_bilibili_video = on_regex(link_metadata.bilibili_vid_pattern, block=True)
@_bilibili_video.handle()
async def _(state: T_State, bot: Bot, event: Event):
    data = await link_metadata.fetch_bilibili_data(state['_matched_groups'][0])
    if data:
        msg = _generate_bilibili_message(data)
        # image message
        if universal_adapters.is_onebot_v11(bot):
            await _bilibili_video.finish(universal_adapters.ob11.Message(f'[CQ:image,file={data["pic"]}]' + msg))
        if universal_adapters.is_onebot_v12(bot):
            await _bilibili_video.finish(universal_adapters.ob12.Message(f'[CQ:image,file={data["pic"]}]' + msg))
        if universal_adapters.is_kook(bot):
            await universal_adapters.send_image_from_url(data["pic"], bot, event)
        await _bilibili_video.finish(msg)

_bilibili_video_short_link = on_regex(r'https:\/\/b23.tv\/(?!BV)[0-9A-Za-z]{7}', block=True)
@_bilibili_video_short_link.handle()
async def _(state: T_State, bot: Bot, event: Event):
    vid = await link_metadata.get_bvid_from_bilibili_short_link(state['_matched_str'])
    data = await link_metadata.fetch_bilibili_data(vid)
    if data:
        msg = _generate_bilibili_message(data)
        # image message
        if universal_adapters.is_onebot_v11(bot):
            await _bilibili_video_short_link.finish(universal_adapters.ob11.Message(f'[CQ:image,file={data["pic"]}]' + msg))
        if universal_adapters.is_onebot_v12(bot):
            await _bilibili_video_short_link.finish(universal_adapters.ob12.Message(f'[CQ:image,file={data["pic"]}]' + msg))
        if universal_adapters.is_kook(bot):
            await universal_adapters.send_image_from_url(data["pic"], bot, event)
        await _bilibili_video_short_link.finish(msg)
