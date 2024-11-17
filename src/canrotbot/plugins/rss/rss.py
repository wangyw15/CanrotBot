from datetime import datetime

import feedparser
from feedparser.util import FeedParserDict
from nonebot_plugin_alconna import Target
from sqlalchemy import delete, insert, select, update

from canrotbot.essentials.libraries import database, network

from .data import RssEntry, RssSubscription


def get_feed_update_time(feed_data: FeedParserDict) -> datetime | None:
    """
    获取RSS订阅的更新时间

    :param feed_data: RSS订阅内容

    :return: 更新时间
    """
    if "updated_parsed" in feed_data.feed:
        return datetime(*feed_data.feed.updated_parsed[:6])
    if "published_parsed" in feed_data.feed:
        return datetime(*feed_data.feed.published_parsed[:6])
    return None


async def fetch_rss(url: str) -> FeedParserDict | None:
    """
    获取RSS订阅内容

    :param url: RSS订阅地址

    :return: RSS订阅内容
    """
    feed_content = await network.fetch_text_data(url)
    if feed_content:
        return feedparser.parse(feed_content)
    return None


async def add_subscription(url: str, target: Target) -> bool:
    """
    添加RSS订阅，不会插入RSS Entry

    :param url: RSS订阅地址
    :param target: 订阅目标

    :return: 是否订阅成功
    """
    with database.get_session().begin() as session:
        subscription = session.execute(
                select(RssSubscription)
                .where(RssSubscription.url == url)
                .where(RssSubscription.private_chat == target.private)
                .where(RssSubscription.channel_chat == target.channel)
                .where(RssSubscription.self_id == target.self_id)
                .where(RssSubscription.platform_id == target.id)
        ).one_or_none()
        # 避免重复订阅
        if subscription:
            return False

        feed_data = await fetch_rss(url)
        if not feed_data:
            return False

        session.execute(
            insert(RssSubscription).values(
                url=url,
                last_update=get_feed_update_time(feed_data),
                title=feed_data.feed.title,
                link=feed_data.feed.link,
                description=feed_data.feed.description,
                private_chat=target.private,
                channel_chat=target.channel,
                self_id=target.self_id,
                platform_id=target.id,
            )
        )
        return True


def delete_subscription(subscription_id: int, target: Target) -> bool:
    """
    删除RSS订阅

    :param subscription_id: 订阅ID
    :param target: 订阅目标

    :return: 是否退订成功
    """
    with database.get_session().begin() as session:
        subscription = session.execute(
            select(RssSubscription)
            .where(RssSubscription.id == subscription_id)
            .where(RssSubscription.private_chat == target.private)
            .where(RssSubscription.channel_chat == target.channel)
            .where(RssSubscription.self_id == target.self_id)
            .where(RssSubscription.platform_id == target.id)
        ).one_or_none()
        # 避免删除不存在的订阅
        if not subscription:
            return False

        session.execute(
            delete(RssSubscription)
            .where(RssSubscription.id == subscription_id)
            .where(RssSubscription.private_chat == target.private)
            .where(RssSubscription.channel_chat == target.channel)
            .where(RssSubscription.self_id == target.self_id)
            .where(RssSubscription.platform_id == target.id)
        )
        return True


def list_target_subscriptions(target: Target) -> list[RssSubscription]:
    """
    列出目标订阅

    :param target: 订阅目标

    :return: 订阅列表
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(RssSubscription)
            .where(RssSubscription.private_chat == target.private)
            .where(RssSubscription.channel_chat == target.channel)
            .where(RssSubscription.self_id == target.self_id)
            .where(RssSubscription.platform_id == target.id)
        ).scalars().all()
        session.expunge_all()
        return list(result)


def list_all_subscriptions() -> list[RssSubscription]:
    """
    列出所有订阅

    :return: 订阅列表
    """
    with database.get_session().begin() as session:
        result = session.execute(select(RssSubscription)).scalars().all()
        session.expunge_all()
        return list(result)


def get_subscription(subscription_id: int) -> RssSubscription | None:
    """
    获取订阅

    :param subscription_id: 订阅ID

    :return: 订阅
    """
    with database.get_session().begin() as session:
        subscription = session.execute(
            select(RssSubscription).where(RssSubscription.id == subscription_id)
        ).scalar_one_or_none()
        session.expunge_all()
        return subscription


def get_subscription_target(subscription_id: int) -> Target | None:
    """
    获取订阅目标

    :param subscription_id: 订阅ID

    :return: 订阅目标
    """
    with database.get_session().begin() as session:
        subscription = session.execute(
            select(RssSubscription)
            .where(RssSubscription.id == subscription_id)
        ).scalar_one_or_none()
        if not subscription:
            return None
        return Target(
            private=subscription.private_chat,
            channel=subscription.channel_chat,
            self_id=subscription.self_id,
            id=subscription.platform_id,
        )


async def update_subscription(subscription_id: int, only_new_entries: bool = False) -> list[RssEntry]:
    """
    更新RSS订阅

    :param subscription_id: 订阅ID
    :param only_new_entries: 是否只返回新的entry

    :return: 更新的entry列表
    """
    with database.get_session().begin() as session:
        subscription = session.execute(
            select(RssSubscription).where(RssSubscription.id == subscription_id)
        ).scalar_one()

        feed_data = await fetch_rss(subscription.url)
        if not feed_data:
            return []

        # 更新feed信息
        session.execute(
            update(RssSubscription)
            .where(RssSubscription.id == subscription_id)
            .values(
                title=feed_data.feed.title,
                link=feed_data.feed.link,
                description=feed_data.feed.description,
                last_update=get_feed_update_time(feed_data),
            )
        )

        # 更新item信息
        entries: list[RssEntry] = []
        for entry in feed_data.entries:
            db_entry = session.execute(
                select(RssEntry)
                .where(RssEntry.subscription_id == subscription_id)
                .where(RssEntry.guid == entry.id)
            ).scalar_one_or_none()

            # 跳过已存在的entry
            if db_entry:
                if not only_new_entries:
                    entries.append(db_entry)
                continue

            new_entry = RssEntry(
                subscription_id=subscription_id,
                title=entry.title,
                link=entry.link,
                description=entry.description,
                guid=entry.id,
                publish_date=datetime(*entry.published_parsed[:6]),
            )
            session.add(new_entry)
            session.flush()
            entries.append(new_entry)

        session.expunge_all()
        return entries
