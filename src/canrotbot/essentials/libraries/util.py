import nonebot.adapters.console as console
import nonebot.adapters.kaiheila as kook

# import nonebot.adapters.mirai2 as mirai2
import nonebot.adapters.onebot.v11 as ob11
import nonebot.adapters.onebot.v12 as ob12
import nonebot.adapters.qq as qq
from nonebot.adapters import Bot, Event
from nonebot.matcher import current_bot
from nonebot_plugin_alconna import UniMessage, SerializeFailed
import warnings

MESSAGE_SPLIT_LINE = "--------------------"
"""
消息分割线
"""


def get_group_id(event: Event) -> str:
    """
    从不同的事件中获取群 ID

    :param event: 事件

    :return: 群 ID (platform_id)
    """
    warnings.warn("util.get_group_id 已弃用，请使用重载处理", DeprecationWarning)
    if isinstance(event, ob11.GroupMessageEvent) or isinstance(
        event, ob12.GroupMessageEvent
    ):
        return "qq_" + str(event.group_id)
    # elif isinstance(event, mirai2.GroupMessage):
    #     return "qq_" + str(event.sender.group.id)
    elif isinstance(event, qq.GroupRobotEvent):
        return "qqbot_" + str(event.group_openid)
    elif isinstance(event, qq.GuildMessageEvent):
        return "qqbot_" + str(event)
    elif isinstance(event, kook.event.ChannelMessageEvent):
        return "kook_" + str(event.group_id)
    elif isinstance(event, console.MessageEvent):
        return "console_0"
    return ""


async def get_bot_name(event: Event, bot: Bot, default: str = None) -> str | None:
    """
    从不同的事件中获取机器人昵称

    :param event: 事件
    :param bot: 机器人
    :param default: 默认值

    :return: 机器人昵称
    """
    warnings.warn("util.get_bot_name 已弃用，请使用重载处理", DeprecationWarning)
    # onebot v11
    if isinstance(bot, ob11.Bot):
        if isinstance(event, ob11.GroupMessageEvent):
            user_info = await bot.get_group_member_info(
                group_id=event.group_id, user_id=event.self_id
            )
            if user_info["card"]:
                return user_info["card"]
            return user_info["nickname"]
        elif isinstance(event, ob11.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self_id)
            return user_info["nickname"]
    # onebot v12
    elif isinstance(bot, ob12.Bot):
        if isinstance(event, ob12.GroupMessageEvent):
            user_info = await bot.get_group_member_info(
                group_id=event.group_id, user_id=event.self.user_id
            )
            if user_info["card"]:
                return user_info["card"]
            return user_info["nickname"]
        elif isinstance(event, ob12.PrivateMessageEvent):
            user_info = await bot.get_stranger_info(user_id=event.self.user_id)
            return user_info["nickname"]
    # mirai2
    # elif isinstance(bot, mirai2.Bot):
    #     if isinstance(event, mirai2.GroupMessage):
    #         user_info = await bot.member_profile(
    #             target=event.sender.group.id, member_id=bot.self_id
    #         )
    #         return user_info["nickname"]
    #     elif isinstance(event, mirai2.FriendMessage):
    #         user_info = bot.bot_pro_file()
    #         return user_info["nickname"]
    # kook
    elif isinstance(bot, kook.Bot):
        if isinstance(event, kook.Event) and hasattr(event, "group_id"):
            user_info = await bot.user_view(
                user_id=bot.self_id, group_id=event.group_id
            )
            return user_info.nickname
    return default


def seconds_to_time(seconds: float) -> str:
    """
    时间戳转换为时间

    :param seconds: 时间戳

    :return: 时间
    """
    warnings.warn("util.seconds_to_time 非通用函数", DeprecationWarning)
    ms = int(seconds % 1 * 1000)
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{str(h).zfill(2)}:{str(m).zfill(2)}:{str(s).zfill(2)}.{str(ms).zfill(3)}"


async def can_send_segment(segment_type: type) -> bool:
    """
    是否可以发送指定类型的消息段

    :param segment_type: 消息段类型

    :return: 是否可以发送
    """
    try:
        await UniMessage(segment_type(raw=b"placeholder")).export(fallback=False)
        return True
    except SerializeFailed:
        return False
    except Exception:
        raise


def is_qq(bot: Bot) -> bool:
    warnings.warn(
        "util.is_qq 已弃用，且不支持 QQ 官方适配器，请使用重载处理", DeprecationWarning
    )
    return (
        isinstance(bot, ob11.Bot)
        or isinstance(bot, ob12.Bot)
        # or isinstance(bot, mirai2.Bot)
    )


def can_send_url() -> bool:
    """
    是否可以发送 URL

    :return: 是否可以发送
    """
    try:
        from nonebot.adapters.qq import Bot as QQBot

        if isinstance(current_bot.get(), QQBot):
            return False
    except ImportError:
        pass
    return True


__all__ = [
    "get_group_id",
    "get_bot_name",
    "seconds_to_time",
    "can_send_segment",
    "is_qq",
    "MESSAGE_SPLIT_LINE",
    "can_send_url",
]
