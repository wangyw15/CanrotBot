# puid (platform user id): qq_1234567890, kook_1234567890, ...
# uid (user id): uuid4
import re
import uuid

import nonebot.adapters.console as console
import nonebot.adapters.kaiheila as kook
import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as ob11
import nonebot.adapters.onebot.v12 as ob12
import nonebot.adapters.qqguild as qqguild
from nonebot.adapters import Bot, Event
from nonebot.matcher import current_bot, current_event
from sqlalchemy import select, delete, insert

from essentials.libraries import util
from storage import database
from . import data


def puid_user_exists(puid: str) -> bool:
    """
    检查给定的puid是否存在

    :param puid: 要检查的puid

    :return: puid是否存在
    """
    with database.get_session().begin() as session:
        query = select(data.Bind).where(data.Bind.platform_user_id == puid)
        result = session.execute(query).first()
        return result is not None


def uid_user_exists(uid: str) -> bool:
    """
    检查给定的uid是否存在

    :param uid: 要检查的uid

    :return: uid是否存在
    """
    with database.get_session().begin() as session:
        query = select(data.User).where(data.User.user_id == uid)
        result = session.execute(query).first()
        return result is not None


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
    with database.get_session().begin() as session:
        session.execute(insert(data.Bind).values(platform_user_id=puid, user_id=uid))
        session.commit()
    return True


def unbind(puid: str) -> bool:
    """
    puid解绑

    :param puid: 要解绑的puid

    :return: 是否成功解绑
    """
    if not puid_user_exists(puid):
        return False
    with database.get_session().begin() as session:
        query = delete(data.Bind).where(data.Bind.platform_user_id == puid)
        session.execute(query)
        session.commit()
    return True


def register(puid: str) -> str:
    """
    注册新用户，并且自动绑定puid

    :param puid: 要注册的puid

    :return: uid
    """
    if puid_user_exists(puid):
        return ""
    uid = str(uuid.uuid4())
    with database.get_session().begin() as session:
        session.execute(insert(data.User).values(user_id=uid))
        session.execute(insert(data.Bind).values(platform_user_id=puid, user_id=uid))
        session.commit()
    return uid


async def get_puid(bot: Bot | None = None, event: Event | None = None) -> str:
    """
    获取puid

    :param bot: Bot
    :param event: Event

    :return: puid
    """
    if not bot:
        bot = current_bot.get()
    if not event:
        event = current_event.get()
    puid = event.get_user_id()
    if await util.is_qq(bot):
        puid = "qq_" + puid
    elif isinstance(bot, kook.Bot):
        puid = "kook_" + puid
    elif isinstance(bot, console.Bot):
        puid = "console_0"
    elif isinstance(bot, qqguild.Bot):
        puid = "qqguild_" + puid
    return puid


async def get_uid(puid: str = "") -> str:
    """
    查询puid对应的uid

    :param puid: 要查询的puid，为空则自动获取

    :return: uid
    """
    if not puid:
        puid = await get_puid()
    elif not puid_user_exists(puid):
        return ""
    with database.get_session().begin() as session:
        query = select(data.Bind).where(data.Bind.platform_user_id == puid)
        result = session.execute(query).scalar_one()
        return result.user_id


def check_puid_validation(puid: str) -> bool:
    """检查puid是否有效"""
    return re.match("^[a-z]+_[0-9]+$", puid) is not None


def get_bind_by_uid(uid: str) -> list[str]:
    """
    查询uid绑定的puid

    :param uid: 要查询的uid

    :return: puid列表
    """
    with database.get_session().begin() as session:
        query = select(data.Bind).where(data.Bind.user_id == uid)
        result = session.execute(query).scalars().all()
        return [_bind.platform_user_id for _bind in result]


async def get_bind_by_puid(puid: str) -> list[str]:
    """
    查询puid对应的uid所绑定的puid

    :param puid: 要查询的puid

    :return: puid列表
    """
    return get_bind_by_uid(await get_uid(puid))


async def get_user_name(
    event: Event | None = None, bot: Bot | None = None, default: str = None
) -> str | None:
    """
    从不同的事件中获取用户昵称

    :param event: 事件
    :param bot: Bot对象
    :param default: 默认值

    :return: 用户昵称
    """
    # onebot v11
    if not bot:
        bot = current_bot.get()
    if not event:
        event = current_event.get()
    if isinstance(bot, ob11.Bot):
        if isinstance(event, ob11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(
                group_id=event.group_id, user_id=event.user_id
            )
            if user_info["card"]:
                return user_info["card"]
            return user_info["nickname"]
        elif isinstance(event, ob11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info["nickname"]
    # onebot v12
    elif isinstance(bot, ob12.Bot):
        if isinstance(event, ob12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(
                group_id=event.group_id, user_id=event.user_id
            )
            if user_info["card"]:
                return user_info["card"]
            return user_info["nickname"]
        elif isinstance(event, ob12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.user_id)
            return user_info["nickname"]
    # mirai2
    elif isinstance(bot, mirai2.Bot):
        if isinstance(event, mirai2.GroupMessage):
            resp = await bot.member_list(target=event.sender.group.id)
            if resp["code"] == 0 and "data" in resp:
                for member in resp["data"]:
                    if member["id"] == event.sender.id:
                        return member["memberName"]
        elif isinstance(event, mirai2.FriendMessage):
            return event.sender.nickname
    # kook
    elif isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event) and hasattr(event, "extra"):
            return event.extra.author.nickname
    return default
