from arclet.alconna import Alconna
from nonebot import logger
from nonebot.adapters.qq import Bot as QQBot
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    CommandMeta,
    MsgTarget,
    Subcommand,
    Target,
    Text,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_apscheduler import scheduler
from sqlalchemy import delete, insert, select

from canrotbot.essentials.libraries import database

from . import daily_news
from .data import Subscribers

WITHOUT_URL_FLAG = "WITHOUT_URL"


daily_news_command = Alconna(
    "daily",
    Subcommand(
        "subscribe",
        alias=["订阅"],
    ),
    Subcommand(
        "unsubscribe",
        alias=["退订"],
    ),
    meta=CommandMeta(description="每日新闻，可以订阅，早上八点推送"),
)

__plugin_meta__ = PluginMetadata(
    name="看新闻",
    description=daily_news_command.meta.description,
    usage=daily_news_command.get_help(),
    config=None,
)


daily_news_matcher = on_alconna(
    daily_news_command,
    aliases={"每日新闻"},
    block=True,
)


@daily_news_matcher.assign("subscribe")
async def _(target: MsgTarget):
    with database.get_session().begin() as session:
        session.execute(
            insert(Subscribers).values(
                private_chat=target.private,
                channel_chat=target.channel,
                self_id=target.self_id,
                platform_id=target.id,
            )
        )
    await daily_news_matcher.finish("每日新闻订阅成功")


@daily_news_matcher.assign("unsubscribe")
async def _(target: MsgTarget):
    try:
        with database.get_session().begin() as session:
            session.execute(
                delete(Subscribers).where(
                    Subscribers.private_chat == target.private,
                    Subscribers.channel_chat == target.channel,
                    Subscribers.self_id == target.self_id,
                    Subscribers.platform_id == target.id,
                )
            )
        await daily_news_matcher.finish("每日新闻退订成功")
    except ValueError:
        await daily_news_matcher.finish("每日新闻未订阅")


@daily_news_matcher.handle()
async def _(state: T_State, bot: QQBot):
    _ = bot.self_id
    state[WITHOUT_URL_FLAG] = True


@daily_news_matcher.handle()
async def _(state: T_State):
    if news := await daily_news.get_daily_news():
        logger.info("News fetch success")
        await daily_news_matcher.finish(
            daily_news.generate_news_message(
                news, not state.get(WITHOUT_URL_FLAG, False)
            )
        )
    else:
        logger.error("News fetch failed")
        await daily_news_matcher.finish("获取新闻失败")


@scheduler.scheduled_job("cron", hour="8", id="daily_news")
async def _():
    if news := await daily_news.get_daily_news():
        logger.info("News fetch success")
        news_text = daily_news.generate_news_message(news)
    else:
        logger.error("News fetch failed")
        news_text = "获取新闻失败"

    with database.get_session().begin() as session:
        _subscribers = session.execute(select(Subscribers)).scalars().all()
        for subscriber in _subscribers:
            target = Target(
                id=subscriber.platform_id,
                self_id=subscriber.self_id,
                private=subscriber.private_chat,
                channel=subscriber.channel_chat,
            )
            await UniMessage(Text(news_text)).send(target)
            logger.info(
                f"News sent to {subscriber.platform_id} at {subscriber.self_id}"
            )
