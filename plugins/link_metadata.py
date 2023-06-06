from nonebot import on_regex
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
import datetime

from ..libraries import link_metadata
from ..adapters import unified

__plugin_meta__ = PluginMetadata(
    name='链接元数据',
    description='获取链接指向的内容',
    usage='发送支持解析的链接会自动触发',
    config=None
)


def _generate_bilibili_message(data: dict) -> str:
    # either use the first line of description or the first 50 characters of description
    desc = '\n'.join([x.strip() for x in data['desc'].split('\n') if x.strip() != ''])
    if len(desc) > 200:
        desc = desc[:200] + '...'
    # publish time
    date = datetime.datetime.fromtimestamp(data['pubdate'])
    # generate message
    msg = f'标题: \n{data["title"]}\n' \
          f'UP主: \n{data["owner"]["name"]}\n' \
          f'发布时间: {date.strftime("%Y年%m月%d日 %H:%M:%S")}\n' \
          f'播放: {data["stat"]["view"]}\n' \
          f'弹幕: {data["stat"]["danmaku"]}\n' \
          f'点赞: {data["stat"]["like"]}\n' \
          f'投币: {data["stat"]["coin"]}\n' \
          f'简介:\n{desc}\n' \
          f'视频链接: \nhttps://www.bilibili.com/video/{data["bvid"]}'
    return msg


def _generate_youtube_message(data: dict) -> str:
    # either use the first line of description or the first 50 characters of description
    desc = '\n'.join([x.strip() for x in data['snippet']['description'].split('\n') if x.strip() != ''])
    if len(desc) > 200:
        desc = desc[:200] + '...'
    # publish time
    date = datetime.datetime.strptime(data['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=8)
    # generate message
    msg = f'标题: \n{data["snippet"]["title"]}\n' \
          f'频道: \n{data["snippet"]["channelTitle"]}\n' \
          f'发布时间: {date.strftime("%Y年%m月%d日 %H:%M:%S")}\n' \
          f'播放: {data["statistics"]["viewCount"]}\n' \
          f'点赞: {data["statistics"]["likeCount"]}\n' if 'likeCount' in data["statistics"] else '' \
          f'评论: {data["statistics"]["commentCount"]}\n' \
          f'简介:\n{desc}\n' \
          f'视频链接: \nhttps://youtu.be/{data["id"]}'
    return msg


_bilibili_video = on_regex(link_metadata.bilibili_vid_pattern, block=True)
@_bilibili_video.handle()
async def _(state: T_State, bot: Bot, event: Event):
    data = await link_metadata.fetch_bilibili_data(state['_matched_groups'][0])
    if data:
        msg = _generate_bilibili_message(data)
        final_msg = unified.Message()
        final_msg.append(unified.MessageSegment.image(data['pic'], '视频封面图'))
        final_msg.append(msg)
        await final_msg.send(bot, event)
        await _bilibili_video.finish()


_bilibili_video_short_link = on_regex(r'https:\/\/b23.tv\/(?!BV)[0-9A-Za-z]{7}', block=True)
@_bilibili_video_short_link.handle()
async def _(state: T_State, bot: Bot, event: Event):
    vid = await link_metadata.get_bvid_from_bilibili_short_link(state['_matched_str'])
    if vid:
        data = await link_metadata.fetch_bilibili_data(vid)
        if data:
            msg = _generate_bilibili_message(data)
            final_msg = unified.Message()
            final_msg.append(unified.MessageSegment.image(data['pic'], '视频封面图'))
            final_msg.append(msg)
            await final_msg.send(bot, event)
            await _bilibili_video_short_link.finish()


_youtube_video = on_regex(link_metadata.youtube_id_pattern, block=True)
@_youtube_video.handle()
async def _(state: T_State, bot: Bot, event: Event):
    data = await link_metadata.fetch_youtube_data(state['_matched_groups'][0])
    if data:
        msg = _generate_youtube_message(data)
        img_data = await link_metadata.fetch_youtube_thumbnail(data)
        final_msg = unified.Message()
        final_msg.append(unified.MessageSegment.image(img_data, '视频封面图'))
        final_msg.append(msg)
        await final_msg.send(bot, event)
        await _youtube_video.finish()
