from typing import cast

import nonebot.adapters.console as console
import nonebot.adapters.kaiheila as kook

# import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as ob11
import nonebot.adapters.onebot.v12 as ob12
import nonebot.adapters.qq as qq
from nonebot.adapters import Bot, Event
from nonebot.matcher import current_bot, current_event
from sqlalchemy import select, delete, insert, ColumnElement

from . import data, snowflake
from .. import database


def platform_id_user_exists(platform_id: str) -> bool:
    """
    检查给定的platform_id是否已注册

    :param platform_id: 要检查的platform_id

    :return: platform_id是否已注册
    """
    with database.get_session().begin() as session:
        query = select(data.Bind).where(
            cast(ColumnElement[bool], data.Bind.platform_id == platform_id)
        )
        result = session.execute(query).first()
        return result is not None


def uid_user_exists(uid: int) -> bool:
    """
    检查给定的uid是否存在

    :param uid: 要检查的uid

    :return: uid是否存在
    """
    with database.get_session().begin() as session:
        query = select(data.User).where(cast(ColumnElement[bool], data.User.id == uid))
        result = session.execute(query).first()
        return result is not None


def bind(platform_id: str, uid: int) -> bool:
    """
    将platform_id绑定到uid

    :param platform_id: 被绑定的platform_id
    :param uid: 要绑定到的uid

    :return: 是否成功绑定
    """
    if not uid_user_exists(uid):
        return False
    if platform_id_user_exists(platform_id):
        return False
    with database.get_session().begin() as session:
        session.execute(insert(data.Bind).values(platform_id=platform_id, user_id=uid))
        session.commit()
    return True


def unbind(platform_id: str) -> bool:
    """
    platform_id解绑

    :param platform_id: 要解绑的platform_id

    :return: 是否成功解绑
    """
    if not platform_id_user_exists(platform_id):
        return False
    with database.get_session().begin() as session:
        query = delete(data.Bind).where(
            cast(ColumnElement[bool], data.Bind.platform_id == platform_id)
        )
        session.execute(query)
        session.commit()
    return True


def register(platform_id: str) -> int:
    """
    注册新用户，并且自动绑定platform_id

    :param platform_id: 要注册的platform_id

    :return: 新用户的uid，如果platform_id已注册则返回0
    """
    if platform_id_user_exists(platform_id):
        return 0
    uid = snowflake.generate_id()
    with database.get_session().begin() as session:
        session.execute(insert(data.User).values(id=uid))
        session.execute(insert(data.Bind).values(platform_id=platform_id, user_id=uid))
        session.commit()
    return uid


def get_uid(platform_id: str = "") -> int:
    """
    查询platform_id对应的uid

    :param platform_id: 要查询的platform_id，为空则自动获取

    :return: uid
    """
    if not platform_id:
        platform_id = current_event.get().get_user_id()
    if not platform_id_user_exists(platform_id):
        return 0
    with database.get_session().begin() as session:
        query = select(data.Bind).where(
            cast(ColumnElement[bool], data.Bind.platform_id == platform_id)
        )
        result = session.execute(query).scalar_one()
        return result.user_id


def get_bind_by_uid(uid: int) -> list[str]:
    """
    查询uid绑定的platform_id

    :param uid: 要查询的uid

    :return: platform_id列表
    """
    with database.get_session().begin() as session:
        query = select(data.Bind).where(
            cast(ColumnElement[bool], data.Bind.user_id == uid)
        )
        result = session.execute(query).scalars().all()
        return [_bind.platform_id for _bind in result]


def get_bind_by_platform_id(platform_id: str) -> list[str]:
    """
    查询platform_id对应的uid所绑定的platform_id

    :param platform_id: 要查询的platform_id

    :return: platform_id列表
    """
    return get_bind_by_uid(get_uid(platform_id))


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
    if not bot:
        bot = current_bot.get()
    if not event:
        event = current_event.get()
    # onebot v11
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
    # elif isinstance(bot, mirai2.Bot):
    #     if isinstance(event, mirai2.GroupMessage):
    #         resp = await bot.member_list(target=event.sender.group.id)
    #         if resp["code"] == 0 and "data" in resp:
    #             for member in resp["data"]:
    #                 if member["id"] == event.sender.id:
    #                     return member["memberName"]
    #     elif isinstance(event, mirai2.FriendMessage):
    #         return event.sender.nickname
    # kook
    elif isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event) and hasattr(event, "extra"):
            return event.extra.author.nickname
    # qq
    elif isinstance(bot, qq.Bot):
        if member := getattr(event, "member", None):
            if nickname := getattr(member, "nick", None):
                return nickname
        if author := getattr(event, "author", None):
            if username := getattr(author, "username", None):
                return username
    # console
    elif isinstance(bot, console.Bot):
        if isinstance(event, console.MessageEvent):
            return event.user.nickname

    return default
