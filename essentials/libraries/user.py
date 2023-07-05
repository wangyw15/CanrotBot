# puid (platform user id): qq_1234567890, kook_1234567890, ...
# uid (user id): uuid4
# 按道理来说应该要缓存一下文件指针，但是大概提升不了多少性能（毕竟没那么多并发
import json
import re
import typing
import uuid
from pathlib import Path

from nonebot.adapters import Bot, Event

from adapters import unified
from . import storage

TData = typing.TypeVar('TData', bound=typing.Union[list, dict])


class UserDataStorage(typing.Generic[TData]):
    def __init__(self, storage_name: str):
        self.__storage_name: str = storage_name
        self.__data: dict[str] = {}
        self.__base_path: Path = storage.get_path(self.__storage_name)
        # 自动创建文件夹
        if not self.__base_path.exists():
            self.__base_path.mkdir(parents=True, exist_ok=True)
        # 加载数据
        for i in storage.get_path(self.__storage_name).iterdir():
            if i.is_file() and i.suffix == '.json':
                self.__data[i.stem] = json.loads(i.read_text(encoding='utf-8'))

    def _write(self, file_name: str, obj: TData):
        path = self.__base_path / f'{file_name}.json'
        path.write_text(json.dumps(obj, indent=4, ensure_ascii=False), encoding='utf-8')

    @property
    def storage_name(self):
        return self.__storage_name

    @property
    def data(self):
        return self.__data

    def __contains__(self, file_name: str):
        return file_name in self.__data

    def __getitem__(self, file_name: str) -> typing.Union[TData, None]:
        if file_name not in self.__data:
            return None
        return self.__data[file_name]

    def __setitem__(self, file_name: str, obj: TData):
        self.__data[file_name] = obj
        self._write(file_name, obj)

    def save(self):
        """
        保存所有数据
        """
        for file_name, data in self.__data.items():
            self._write(file_name, data)

    def open(self, file_name: str) -> typing.IO:
        """
        打开文件

        :param file_name: 文件名

        :return: 文件指针
        """
        path = self.__base_path / file_name
        return path.open('w+b')

    def exists(self, file_name: str) -> bool:
        """
        检查文件是否存在

        :param file_name: 文件名

        :return: 文件是否存在
        """
        return (self.__base_path / file_name).exists()


_user_data = UserDataStorage[dict[str]]('user')


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
