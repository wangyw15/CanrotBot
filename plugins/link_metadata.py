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

_bilibili_video = on_regex(r'(?:https?:\/\/)?(?:www\.)?bilibili.com\/video\/((?:BV|av)[0-9A-Za-z]+)', block=True)
@_bilibili_video.handle()
async def _(state: T_State, bot: Bot, event: Event):
    vid = state['_matched_groups'][0]
    if vid.startswith('BV'):
        data = await link_metadata.fetch_bilibili_data(vid, 'bv')
    elif vid.startswith('av'):
        data = await link_metadata.fetch_bilibili_data(vid, 'av')
    if data:
        msg = f'标题: \n{data["title"]}\nUP主: \n{data["owner"]["name"]}\n播放: {data["stat"]["view"]}\n弹幕: {data["stat"]["danmaku"]}\n点赞: {data["stat"]["like"]}\n投币: {data["stat"]["coin"]}\n简介: \n{data["desc"]}'
        if universal_adapters.is_onebot_v11(bot):
            await _bilibili_video.finish(universal_adapters.ob11.Message(f'[CQ:image,file={data["pic"]}]' + msg))
        if universal_adapters.is_onebot_v12(bot):
            await _bilibili_video.finish(universal_adapters.ob12.Message(f'[CQ:image,file={data["pic"]}]' + msg))
        if universal_adapters.is_kook(bot):
            await universal_adapters.send_image_from_url(data["pic"], bot, event)
        await _bilibili_video.finish(msg)
