import datetime
import typing

from nonebot import on_regex
from nonebot.params import RegexGroup
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import UniMsg, Image

from essentials.libraries import util
from .youtube import youtube_id_pattern, fetch_youtube_data, fetch_youtube_thumbnail

__plugin_meta__ = PluginMetadata(
    name='链接元数据',
    description='获取链接指向的内容',
    usage='发送支持解析的链接会自动触发',
    config=None
)


def _generate_youtube_message(data: dict) -> str:
    # 选择第一行或者前200个字符
    desc = '\n'.join([x.strip() for x in data['snippet']['description'].split('\n') if x.strip() != ''])
    if len(desc) > 200:
        desc = desc[:200] + '...'
    # 发布时间
    date = datetime.datetime.strptime(data['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')+datetime.timedelta(hours=8)
    # 生成信息
    msg = ''
    msg += f'标题: \n{data["snippet"]["title"]}\n' \
           f'频道: \n{data["snippet"]["channelTitle"]}\n' \
           f'发布时间: {date.strftime("%Y年%m月%d日 %H:%M:%S")}\n' \
           f'播放: {data["statistics"]["viewCount"]}\n'
    msg += f'点赞: {data["statistics"]["likeCount"]}\n' if 'likeCount' in data['statistics'] else ''
    msg += f'评论: {data["statistics"]["commentCount"]}\n' if 'commentCount' in data['statistics'] else ''
    msg += f'简介:\n{desc}\n' \
           f'视频链接: \nhttps://youtu.be/{data["id"]}'
    return msg


_youtube_video = on_regex(youtube_id_pattern, block=True)


@_youtube_video.handle()
async def _(reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()]):
    data = await fetch_youtube_data(reg[0])
    if data:
        msg = _generate_youtube_message(data)
        final_msg = UniMsg()
        if await util.can_send_segment(Image):
            img_data = await fetch_youtube_thumbnail(data)
            if img_data:
                final_msg.append(Image(raw=img_data))
        final_msg.append(msg)
        await _youtube_video.finish(await final_msg.export())
