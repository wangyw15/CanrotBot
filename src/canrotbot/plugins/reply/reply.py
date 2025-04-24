import random

from nonebot import get_plugin_config
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna import (
    Target,
    get_target,
)
from sqlalchemy import insert, select, update

from canrotbot.essentials.libraries import database

from .arrisa import generate_response as arrisa_response
from .config import ReplyConfig
from .data import ReplyGroupSettings
from .model import ReplyMode

UNKNOWN_RESPONSE: str = "{me}不知道怎么回答{name}喵~"
BOT_NAME: str = "我"
SENDER_NAME: str = "主人"

reply_config = get_plugin_config(ReplyConfig)

# 加载数据
# _reply_data: list[dict[str, str | None]] = file.read_json(
#     path.get_asset_path() / "reply.json"
# )


def is_regex_pattern(content: str) -> bool:
    """
    判断是否为正则表达式

    :param content: 要判断的内容

    :return: 是否为正则表达式
    """
    return content.startswith("/") and content.endswith("/") and len(content) > 2


def get_response(msg: str, mode: ReplyMode = ReplyMode.ARRISA) -> str:
    """
    生成回复

    :param msg: 要回复的内容
    :param mode: 回复模式

    :return: 回复内容
    """
    if mode == ReplyMode.ARRISA:
        return arrisa_response(msg)
    raise ValueError(f"Reply mode {mode} does not exist.")


def get_reply_rate(target: Target) -> float:
    """
    获取群自动回复概率

    :param target: 消息目标

    :return: 概率
    """
    with database.get_session().begin() as session:
        # 不存在配置则使用默认配置
        result = session.execute(
            select(ReplyGroupSettings)
            .where(ReplyGroupSettings.platform_id == target.id)
            .where(ReplyGroupSettings.self_id == target.self_id)
            .where(ReplyGroupSettings.channel_chat == target.channel)
            .where(ReplyGroupSettings.private_chat == target.private)
        ).scalar_one_or_none()
        if result is None:
            return reply_config.default_rate
        return result.rate


def set_reply_rate(target: Target, rate: float):
    """
    设置群自动回复概率

    :param target: 消息目标
    :param rate: 概率

    :return: 是否设置成功
    """
    if 0 <= rate <= 1:
        query = (
            select(ReplyGroupSettings)
            .where(ReplyGroupSettings.platform_id == target.id)
            .where(ReplyGroupSettings.self_id == target.self_id)
            .where(ReplyGroupSettings.channel_chat == target.channel)
            .where(ReplyGroupSettings.private_chat == target.private)
        )
        with database.get_session().begin() as session:
            if session.execute(query).first() is None:
                session.execute(
                    insert(ReplyGroupSettings).values(
                        platform_id=target.id,
                        self_id=target.self_id,
                        channel_chat=target.channel,
                        private_chat=target.private,
                        rate=rate,
                    )
                )
            else:
                session.execute(
                    update(ReplyGroupSettings)
                    .where(ReplyGroupSettings.platform_id == target.id)
                    .where(ReplyGroupSettings.self_id == target.self_id)
                    .where(ReplyGroupSettings.channel_chat == target.channel)
                    .where(ReplyGroupSettings.private_chat == target.private)
                    .values(rate=rate)
                )


def get_reply_mode(target: Target) -> ReplyMode:
    """
    获取群自动回复模式

    :param target: 消息目标

    :return: 模式
    """
    with database.get_session().begin() as session:
        # 不存在配置则使用默认配置
        result = session.execute(
            select(ReplyGroupSettings)
            .where(ReplyGroupSettings.platform_id == target.id)
            .where(ReplyGroupSettings.self_id == target.self_id)
            .where(ReplyGroupSettings.channel_chat == target.channel)
            .where(ReplyGroupSettings.private_chat == target.private)
        ).scalar_one_or_none()
        if result is None:
            return reply_config.default_mode
        return result.mode


def set_reply_mode(target: Target, mode: ReplyMode):
    """
    设置群自动回复模式

    :param target: 消息目标
    :param mode: 模式
    """
    query = (
        select(ReplyGroupSettings)
        .where(ReplyGroupSettings.platform_id == target.id)
        .where(ReplyGroupSettings.self_id == target.self_id)
        .where(ReplyGroupSettings.channel_chat == target.channel)
        .where(ReplyGroupSettings.private_chat == target.private)
    )
    with database.get_session().begin() as session:
        if session.execute(query).first() is None:
            session.execute(
                insert(ReplyGroupSettings).values(
                    platform_id=target.id,
                    self_id=target.self_id,
                    channel_chat=target.channel,
                    private_chat=target.private,
                    mode=mode,
                )
            )
        else:
            session.execute(
                update(ReplyGroupSettings)
                .where(ReplyGroupSettings.platform_id == target.id)
                .where(ReplyGroupSettings.self_id == target.self_id)
                .where(ReplyGroupSettings.channel_chat == target.channel)
                .where(ReplyGroupSettings.private_chat == target.private)
                .values(mode=mode)
            )


def check_reply(bot: Bot, event: Event) -> bool:
    """
    检查是否可以自动回复

    :param bot: 机器人
    :param event: 事件

    :return: 是否可以自动回复
    """
    target = get_target(event, bot)
    if not target.private:  # 确保是群消息
        if random.random() < get_reply_rate(target):
            return True
    return False
