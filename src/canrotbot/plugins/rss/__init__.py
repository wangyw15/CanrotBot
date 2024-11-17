from nonebot import get_app, get_bot, logger, get_plugin_config
from nonebot.adapters.qq import Bot as QQBot
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    MsgTarget,
    Query,
    Subcommand,
    UniMessage,
    on_alconna,
    Target,
)
from nonebot_plugin_apscheduler import scheduler

from .config import RssConfig
from . import rss
from .data import RssSubscription

rss_config = get_plugin_config(RssConfig)

rss_command = Alconna(
    "rss",
    Subcommand("subscribe", Args["subscribe_url", str], alias={"订阅", "sub"}, help_text="订阅RSS"),
    Subcommand("unsubscribe", Args["unsubscribe_id", int], alias={"退订", "unsub"}, help_text="退订RSS"),
    Subcommand("list", help_text="列出RSS订阅"),
    Subcommand("update", Args["update_id", int, -1], alias={"更新"}, help_text="手动更新RSS订阅"),
    meta=CommandMeta(description="提供RSS订阅推送功能"),
)

__plugin_meta__ = PluginMetadata(
    name="RSS",
    description=rss_command.meta.description,
    usage=rss_command.get_help(),
    config=RssConfig,
)

rss_matcher = on_alconna(
    rss_command,
    block=True,
)


@rss_matcher.assign("subscribe")
async def _(target: MsgTarget, subscribe_url: Query[str] = Query("subscribe_url")):
    if await rss.add_subscription(subscribe_url.result, target):
        await rss_matcher.finish("订阅成功")
    await rss_matcher.finish("订阅失败，可能订阅地址已存在或地址无效")


@rss_matcher.assign("unsubscribe")
async def _(target: MsgTarget, unsubscribe_id: Query[int] = Query("unsubscribe_id")):
    if rss.delete_subscription(unsubscribe_id.result, target):
        await rss_matcher.finish("退订成功")
    await rss_matcher.finish("退订失败，订阅id不存在")


@rss_matcher.assign("list")
async def _(target: MsgTarget):
    subscriptions = rss.list_target_subscriptions(target)
    if not subscriptions:
        await rss_matcher.finish("没有已订阅的RSS")
    await rss_matcher.finish("\n".join([f"{i.id}: {i.title} - {i.url}" for i in subscriptions]))


@rss_matcher.assign("update")
async def _(target: MsgTarget, update_id: Query[int] = Query("update_id", -1)):
    if update_id.result == -1:
        to_be_updated = [i.id for i in rss.list_target_subscriptions(target)]
    else:
        if not rss.get_subscription(update_id.result):
            await rss_matcher.finish("订阅id不存在")
        to_be_updated = [update_id.result]
    await update(to_be_updated)
    await rss_matcher.finish("更新完成")


@scheduler.scheduled_job("interval", seconds=rss_config.interval, id="rss_update")
async def update(subscription_ids: list[int] | None = None):
    logger.info("Updating RSS...")
    if subscription_ids:
        subscriptions: list[RssSubscription] = []
        for i in subscription_ids:
            if subscription := rss.get_subscription(i):
                subscriptions.append(subscription)
    else:
        subscriptions = rss.list_all_subscriptions()

    for subscription in subscriptions:
        entries = await rss.update_subscription(subscription.id, True)
        if not entries:
            continue

        msg = f"{subscription.title}\n"
        for i, entry in enumerate(entries):
            msg += f"{i+1}.\n{entry.title}\n{entry.link}\n\n"

        await UniMessage(msg.strip()).send(rss.get_subscription_target(subscription.id))
