# puid (platform user id): qq_1234567890, kook_1234567890, ...
# uid (user id): uuid4
# 按道理来说应该要缓存一下文件指针，但是大概提升不了多少性能（毕竟没那么多并发
import re
import uuid

from nonebot.adapters import Bot, Event

from adapters import unified
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


def remove_data(uid: str, key: str):
    """
    删除用户数据项

    :param uid: uid
    :param key: 键
    """
    if not puid_user_exists(uid):
        return
    if uid not in _user_data:
        return
    if key not in _user_data[uid]:
        return
    del _user_data[uid][key]
    _user_data.save()


def get_all_data(uid: str) -> dict[str, str]:
    """
    获取所有用户数据项

    :param uid: uid

    :return: 数据
    """
    if not uid_user_exists(uid):
        return {}
    if uid not in _user_data:
        return {}
    return _user_data[uid]
