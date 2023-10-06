from typing import Annotated

from nonebot import on_shell_command, get_bot, require
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata
from sqlalchemy import select, delete, insert

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from adapters import unified
from essentials.libraries import util
from storage import database
from . import data

__plugin_meta__ = PluginMetadata(
    name='看新闻',
    description='每日新闻，订阅功能仅支持 OneBot v11 的机器人',
    usage='/<daily|新闻|每日新闻>',
    config=None
)


_img_url = 'https://api.03c3.cn/zb/'


daily = on_shell_command('daily', aliases={'每日新闻', '新闻'}, block=True)


@daily.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 0:
        await unified.MessageSegment.image(_img_url, '每日新闻图片').send()
        await daily.finish()
    elif len(args) == 1:
        if args[0].lower() == 'subscribe' or args[0] == '订阅':
            if unified.Detector.is_onebot_v11(bot):
                bot_id = bot.self_id
                gid = util.get_group_id(event).split('_')[1]
                with database.get_session() as session:
                    session.execute(insert(data.Subscribers).values(group_id=gid, bot=bot_id))
                    session.commit()
                await daily.finish('每日新闻订阅成功')
            else:
                await daily.finish('该功能仅支持 OneBot v11')
        elif args[0].lower() == 'unsubscribe' or args[0] == '退订':
            if unified.Detector.is_onebot_v11(bot):
                bot_id = bot.self_id
                gid = util.get_group_id(event).split('_')[1]
                try:
                    with database.get_session().begin() as session:
                        session.execute(delete(data.Subscribers).
                                        where(data.Subscribers.group_id == gid, data.Subscribers.bot == bot_id))
                        session.commit()
                    await daily.finish('每日新闻退订成功')
                except ValueError:
                    await daily.finish('每日新闻未订阅')
            else:
                await daily.finish('该功能仅支持 OneBot v11')
        else:
            await daily.finish('用法: ' + __plugin_meta__.usage)


@scheduler.scheduled_job("cron", hour="10", id="daily_news")
async def _():
    with database.get_session().begin() as session:
        _subscribers = session.execute(select(data.Subscribers)).scalars().all()
        for subscriber in _subscribers:
            try:
                bot = get_bot(str(subscriber.bot))
                await bot.call_api('send_group_msg', group_id=subscriber.group_id, message=f'[CQ:image,file={_img_url}]')
            except KeyError:
                pass
