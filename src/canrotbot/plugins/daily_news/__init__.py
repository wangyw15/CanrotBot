import nonebot.adapters.onebot.v11 as ob11
from arclet.alconna import Alconna
from nonebot import get_bot
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Image, Option, UniMessage
from nonebot_plugin_apscheduler import scheduler
from sqlalchemy import select, delete, insert

from canrotbot.essentials.libraries import util, database
from . import data

__plugin_meta__ = PluginMetadata(
    name="看新闻",
    description="每日新闻，订阅功能仅支持 OneBot v11 的机器人",
    usage="/<daily|新闻|每日新闻>",
    config=None,
)


_img_url = "https://api.03c3.cn/zb/"


_command = on_alconna(
    Alconna(
        "每日新闻",
        Option(
            "subscribe",
            alias=["订阅"],
        ),
        Option(
            "unsubscribe",
            alias=["退订"],
        ),
    ),
    block=True,
    aliases={"daily"},
)


@_command.assign("subscribe")
async def _(bot: Bot, event: Event):
    if isinstance(bot, ob11.Bot):
        bot_id = bot.self_id
        gid = util.get_group_id(event).split("_")[1]
        with database.get_session() as session:
            session.execute(insert(data.Subscribers).values(group_id=gid, bot=bot_id))
            session.commit()
        await _command.finish("每日新闻订阅成功")
    else:
        await _command.finish("该功能仅支持 OneBot v11")


@_command.assign("unsubscribe")
async def _(bot: Bot, event: Event):
    if isinstance(bot, ob11.Bot):
        bot_id = bot.self_id
        gid = util.get_group_id(event).split("_")[1]
        try:
            with database.get_session().begin() as session:
                session.execute(
                    delete(data.Subscribers).where(
                        data.Subscribers.platform_id == gid,  # type:ignore
                        data.Subscribers.bot == bot_id,  # type:ignore
                    )
                )
                session.commit()
            await _command.finish("每日新闻退订成功")
        except ValueError:
            await _command.finish("每日新闻未订阅")
    else:
        await _command.finish("该功能仅支持 OneBot v11")


@_command.handle()
async def _():
    if await util.can_send_segment(Image):
        await _command.finish(UniMessage(Image(url=_img_url)))
    else:
        await _command.finish("这里发不了图片哦")


@scheduler.scheduled_job("cron", hour="10", id="daily_news")
async def _():
    with database.get_session().begin() as session:
        _subscribers = session.execute(select(data.Subscribers)).scalars().all()
        for subscriber in _subscribers:
            try:
                bot = get_bot(str(subscriber.bot))
                await bot.call_api(
                    "send_group_msg",
                    group_id=subscriber.platform_id,
                    message=f"[CQ:image,file={_img_url}]",
                )
            except KeyError:
                pass
