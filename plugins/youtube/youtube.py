import datetime

from nonebot import get_plugin_config

from essentials.libraries import network
from .config import YoutubeConfig

YOUTUBE_LINK_PATTERN = r"(?:https?:\/\/)?(?:youtu\.be\/|(?:\w{3}\.)?youtube\.com\/(?:watch\?.*v=|shorts\/))([a-zA-Z0-9-_]+)"
config = get_plugin_config(YoutubeConfig)


async def fetch_youtube_data(ytb_id: str) -> dict:
    if config.api_key:
        data = await network.fetch_json_data(
            f"https://youtube.googleapis.com/youtube/v3/videos?part=snippet%2Cstatistics&id={ytb_id}&key={config.api_key}"
        )
        if data["pageInfo"]["totalResults"] > 0:
            return data["items"][0]
    return {}


async def fetch_youtube_thumbnail(data: dict) -> bytes | None:
    """
    下载 YouTube 封面图

    :param data: YouTube 接口返回的数据

    :return: 封面图数据
    """
    url = ""
    max_width = 0
    for _, v in data["snippet"]["thumbnails"].items():
        if v["width"] > max_width:
            max_width = v["width"]
            url = v["url"]
    return await network.fetch_bytes_data(url)


def generate_youtube_message(data: dict) -> str:
    # 选择第一行或者前200个字符
    desc = "\n".join(
        [
            x.strip()
            for x in data["snippet"]["description"].split("\n")
            if x.strip() != ""
        ]
    )
    if len(desc) > 200:
        desc = desc[:200] + "..."
    # 发布时间
    date = datetime.datetime.strptime(
        data["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
    ) + datetime.timedelta(hours=8)
    # 生成信息
    msg = ""
    msg += (
        f'标题: \n{data["snippet"]["title"]}\n'
        f'频道: \n{data["snippet"]["channelTitle"]}\n'
        f'发布时间: {date.strftime("%Y年%m月%d日 %H:%M:%S")}\n'
        f'播放: {data["statistics"]["viewCount"]}\n'
    )
    msg += (
        f'点赞: {data["statistics"]["likeCount"]}\n'
        if "likeCount" in data["statistics"]
        else ""
    )
    msg += (
        f'评论: {data["statistics"]["commentCount"]}\n'
        if "commentCount" in data["statistics"]
        else ""
    )
    msg += f"简介:\n{desc}\n"

    # 短视频
    if "#shorts" in data["snippet"]["title"]:
        msg += f'视频链接: \nhttps://youtube.com/shorts/{data["id"]}'
    else:
        msg += f'视频链接: \nhttps://youtu.be/{data["id"]}'
    return msg
