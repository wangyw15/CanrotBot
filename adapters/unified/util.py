import re
from typing import Any

import httpx
from nonebot import get_driver
from nonebot.adapters import Bot, Event, MessageSegment

from . import Detector, adapters

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


async def fetch_bytes_data(url: str) -> bytes | None:
    """从URL获取bytes数据"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(url: str) -> Any | None:
    """从URL获取json数据"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


def get_group_id(event: Event) -> str | None:
    """从不同的事件中获取群ID"""
    if isinstance(event, adapters.onebot_v11.GroupMessageEvent) \
            or isinstance(event, adapters.onebot_v12.GroupMessageEvent):
        return str(event.group_id)
    elif isinstance(event, adapters.mirai2.GroupMessage):
        return str(event.sender.group.id)
    elif isinstance(event, adapters.qqguild.Event):
        pass
    elif isinstance(event, adapters.kook.event.ChannelMessageEvent):
        return str(event.group_id)
    return None


async def get_user_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """从不同的事件中获取用户昵称"""
    # onebot v11
    if Detector.is_onebot_v11(bot):
        if isinstance(event, adapters.onebot_v11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, adapters.onebot_v11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info['nickname']
    # onebot v12
    elif Detector.is_onebot_v12(bot):
        if isinstance(event, adapters.onebot_v12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, adapters.onebot_v12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info['nickname']
    # mirai2
    elif Detector.is_mirai2(bot):
        if isinstance(event, adapters.mirai2.GroupMessage):
            return event.sender.name
        elif isinstance(event, adapters.mirai2.FriendMessage):
            return event.sender.nickname
    # kook
    elif Detector.is_kook(bot):
        if isinstance(event, adapters.kook.Event) and hasattr(event, 'extra'):
            return event.extra.author.nickname
    return default


async def get_bot_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """从不同的事件中获取机器人昵称"""
    # onebot v11
    if Detector.is_onebot_v11(bot):
        if isinstance(event, adapters.onebot_v11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, adapters.onebot_v11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self_id)
            return user_info['nickname']
    # onebot v12
    elif Detector.is_onebot_v12(bot):
        if isinstance(event, adapters.onebot_v12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(group_id=event.group_id, user_id=event.self.user_id)
            if user_info['card']:
                return user_info['card']
            return user_info['nickname']
        elif isinstance(event, adapters.onebot_v12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self.user_id)
            return user_info['nickname']
    # mirai2
    elif Detector.is_mirai2(bot):
        if isinstance(event, adapters.mirai2.GroupMessage):
            user_info = await bot.member_profile(target=event.sender.group.id, member_id=bot.self_id)
            return user_info['nickname']
        elif isinstance(event, adapters.mirai2.FriendMessage):
            user_info = bot.bot_pro_file()
            return user_info['nickname']
    # kook
    elif Detector.is_kook(bot):
        if isinstance(event, adapters.kook.Event) and hasattr(event, 'group_id'):
            user_info = await bot.user_view(user_id=bot.self_id, group_id=event.group_id)
            return user_info.nickname
    return default


def is_url(msg: MessageSegment | str) -> bool:
    """检测是否为URL"""
    if isinstance(msg, str):
        return re.match(r'^https?://', msg) is not None
    elif msg.is_text():
        msg = str(msg)
        return re.match(r'^https?://', msg) is not None
    elif isinstance(msg, adapters.kook.MessageSegment):
        if msg.type == 'kmarkdown':
            msg = re.search(r'\[.*]\((\S+)\)', msg.plain_text()).groups()[0]
            return re.match(r'^https?://', msg) is not None
        elif msg.type == 'text':
            return re.match(r'^https?://', msg.plain_text()) is not None
    return False


def seconds_to_time(seconds: float) -> str:
    ms = int(seconds % 1 * 1000)
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}.{str(ms).zfill(3)}"


__all__ = ['fetch_bytes_data',
           'fetch_json_data',
           'get_group_id',
           'get_bot_name',
           'get_user_name',
           'MESSAGE_SPLIT_LINE']
