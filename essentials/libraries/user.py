# puid (platform user id): qq_1234567890, kook_1234567890, ...
# uid (user id): uuid4
# 按道理来说应该要缓存一下文件指针，但是大概提升不了多少性能（毕竟没那么多并发
import re
import uuid

from nonebot import Bot
from nonebot.adapters import Bot, Event
from nonebot.internal.adapter import Event

from adapters import unified
from adapters.unified import Detector, adapters
from . import storage

_user_data = storage.PersistentData[dict[str]]('user')


def puid_user_exists(puid: str) -> bool:
    """
    检查给定的puid是否存在

    :param puid: 要检查的puid

    :return: puid是否存在
    """
    return puid in _user_data['users']


def uid_user_exists(uid: str) -> bool:
    """
    检查给定的uid是否存在

    :param uid: 要检查的uid

    :return: uid是否存在
    """
    return uid in _user_data['users'].values()


def bind(puid: str, uid: str) -> bool:
    """
    将puid绑定到uid

    :param puid: 被绑定的puid
    :param uid: 要绑定到的uid

    :return: 是否成功绑定
    """
    if not uid_user_exists(uid):
        return False
    if puid_user_exists(puid):
        return False
    _user_data['users'][puid] = uid
    _user_data.save()
    return True


def unbind(puid: str) -> bool:
    """
    puid解绑

    :param puid: 要解绑的puid

    :return: 是否成功解绑
    """
    if not puid_user_exists(puid):
        return False
    del _user_data['users'][puid]
    _user_data.save()
    return True


def register(puid: str) -> str:
    """
    注册新用户，并且自动绑定puid

    :param puid: 要注册的puid

    :return: uid
    """
    if puid_user_exists(puid):
        return ''
    uid = str(uuid.uuid4())
    _user_data['users'][puid] = uid
    _user_data.save()
    return uid


def get_puid(bot: Bot, event: Event) -> str:
    """
    获取puid

    :param bot: Bot
    :param event: Event

    :return: puid
    """
    puid = event.get_user_id()
    if unified.Detector.is_onebot_v11(bot) or unified.Detector.is_onebot_v12(bot) or unified.Detector.is_mirai2(bot):
        puid = 'qq_' + puid
    elif unified.Detector.is_kook(bot):
        puid = 'kook_' + puid
    elif unified.Detector.is_console(bot):
        puid = 'console_0'
    elif unified.Detector.is_qqguild(bot):
        puid = 'qqguild_' + puid
    return puid


def get_uid(puid: str) -> str:
    """
    查询puid对应的uid

    :param puid: 要查询的puid

    :return: uid
    """
    if not puid_user_exists(puid):
        return ''
    return _user_data['users'][puid]


def check_puid_validation(puid: str) -> bool:
    """检查puid是否有效"""
    return re.match('^[a-z]+_[0-9]+$', puid) is not None


def get_bind_by_uid(uid: str) -> list[str]:
    """
    查询uid绑定的puid

    :param uid: 要查询的uid

    :return: puid列表
    """
    return [puid for puid, _uid in _user_data['users'].items() if _uid == uid]


def get_bind_by_puid(puid: str) -> list[str]:
    """
    查询puid对应的uid所绑定的puid

    :param puid: 要查询的puid

    :return: puid列表
    """
    return get_bind_by_uid(get_uid(puid))


async def get_user_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """
    从不同的事件中获取用户昵称

    :param event: 事件
    :param bot: Bot对象
    :param default: 默认值

    :return: 用户昵称
    """
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
            resp = bot.member_list(target=event.sender.group.id)
            if resp['code'] == 0 and 'data' in resp:
                for member in resp['data']:
                    if member['id'] == event.sender.id:
                        return member['memberName']
        elif isinstance(event, adapters.mirai2.FriendMessage):
            return event.sender.nickname
    # kook
    elif Detector.is_kook(bot):
        if isinstance(event, adapters.kook.Event) and hasattr(event, 'extra'):
            return event.extra.author.nickname
    return default
