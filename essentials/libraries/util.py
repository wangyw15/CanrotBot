import hashlib
import random
import re
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx
import nonebot.adapters.console as console
import nonebot.adapters.kaiheila as kook
import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as ob11
import nonebot.adapters.onebot.v12 as ob12
import nonebot.adapters.qqguild as qqguild
from nonebot import get_driver
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot_plugin_alconna import UniMessage, SerializeFailed

_driver = get_driver()
_global_config = _driver.config


def _get_config(name: str) -> Any:
    return _global_config.dict()[name]


if proxy := _get_config('canrot_proxy'):
    _client = httpx.AsyncClient(proxies=proxy)
else:
    _client = httpx.AsyncClient()
_client.timeout = 10


MESSAGE_SPLIT_LINE = "--------------------"
"""
消息分割线
"""


async def fetch_bytes_data(url: str, *args, **kwargs) -> bytes | None:
    """
    从 URL 获取 bytes 数据

    :param url: URL
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: bytes 数据
    """
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(url: str, *args, **kwargs) -> Any | None:
    """
    从 URL 获取 json 数据

    :param url: URL
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: json 数据
    """
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def fetch_text_data(url: str, *args, **kwargs) -> str | None:
    """
    从 URL 获取字符串

    :param url: URL
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: 字符串
    """
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.text
    return None


def get_group_id(event: Event) -> str:
    """
    从不同的事件中获取群 ID

    :param event: 事件

    :return: 群 ID (platform_id)
    """
    if isinstance(event, ob11.GroupMessageEvent) or isinstance(event, ob12.GroupMessageEvent):
        return 'qq_' + str(event.group_id)
    elif isinstance(event, mirai2.GroupMessage):
        return 'qq_' + str(event.sender.group.id)
    elif isinstance(event, qqguild.MessageEvent):
        return 'qqguild_' + str(event.channel_id)
    elif isinstance(event, kook.event.ChannelMessageEvent):
        return 'kook_' + str(event.group_id)
    elif isinstance(event, console.MessageEvent):
        return 'console_0'
    return ''


async def get_bot_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """
    从不同的事件中获取机器人昵称

    :param event: 事件
    :param bot: 机器人
    :param default: 默认值

    :return: 机器人昵称
    """
    # onebot v11
    if isinstance(bot, ob11.Bot):
        if isinstance(event, ob11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self_id)
            return user_info['nickname']
    # onebot v12
    elif isinstance(bot, ob12.Bot):
        if isinstance(event, ob12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, ob12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self.user_id)
            return user_info['nickname']
    # mirai2
    elif isinstance(bot, mirai2.Bot):
        if isinstance(event, mirai2.GroupMessage):
            user_info = await bot.member_profile(target=event.sender.group.id, member_id=bot.self_id)
            return user_info['nickname']
        elif isinstance(event, mirai2.FriendMessage):
            user_info = bot.bot_pro_file()
            return user_info['nickname']
    # kook
    elif isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event) and hasattr(event, 'group_id'):
            user_info = await bot.user_view(user_id=bot.self_id, group_id=event.group_id)
            return user_info.nickname
    return default


def is_url(msg: MessageSegment | str) -> bool:
    """
    检测是否为 URL

    :param msg: 消息内容

    :return: 是否为 URL
    """
    if isinstance(msg, str):
        return re.match(r'^https?://', msg) is not None
    elif msg.is_text():
        msg = str(msg)
        return re.match(r'^https?://', msg) is not None
    elif isinstance(msg, kook.MessageSegment):
        if msg.type == 'kmarkdown':
            msg = re.search(r'\[.*]\((\S+)\)', msg.plain_text()).groups()[0]
            return re.match(r'^https?://', msg) is not None
        elif msg.type == 'text':
            return re.match(r'^https?://', msg.plain_text()) is not None
    return False


def seconds_to_time(seconds: float) -> str:
    """
    时间戳转换为时间

    :param seconds: 时间戳

    :return: 时间
    """
    ms = int(seconds % 1 * 1000)
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}.{str(ms).zfill(3)}"


def random_str(length: int) -> str:
    """
    随机字符串，可以用作 id

    :param length: 长度

    :return: 随机字符串
    """
    ret: list[str] = []
    while len(ret) < length:
        ret.extend(hashlib.md5(str(datetime.now().timestamp()).encode(), usedforsecurity=True).hexdigest())
    random.shuffle(ret)
    return ''.join(ret[:length])


def get_iso_time_str(t: datetime | None = None) -> str:
    if not t:
        t = datetime.now()
    return t.astimezone(timezone(timedelta(hours=8))).isoformat()


async def can_send_segment(segment_type: type) -> bool:
    """
    是否可以发送指定类型的消息段

    :param segment_type: 消息段类型

    :return: 是否可以发送
    """
    try:
        await UniMessage(segment_type('')).export(fallback=False)
        return True
    except SerializeFailed:
        return False
    except Exception:
        raise


async def is_qq(bot: Bot) -> bool:
    return isinstance(bot, ob11.Bot) or isinstance(bot, ob12.Bot) or isinstance(bot, mirai2.Bot)


__all__ = ['fetch_bytes_data',
           'fetch_json_data',
           'fetch_text_data',
           'get_group_id',
           'get_bot_name',
           'random_str',
           'MESSAGE_SPLIT_LINE']
