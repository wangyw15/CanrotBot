from typing import Annotated

from nonebot import on_shell_command, require, get_bot
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from ..libraries import universal_adapters
from ..libraries.data import data_cursor


__plugin_meta__ = PluginMetadata(
    name='看新闻',
    description='每日新闻，订阅功能仅支持 OneBot v11 的机器人',
    usage='/<daily|新闻|每日新闻>',
    config=None
)


img_url = 'https://api.03c3.cn/zb/'
data_cursor.execute('CREATE TABLE IF NOT EXISTS daily_subscribers (id INTEGER PRIMARY KEY, bot INTEGER)')


daily = on_shell_command('daily', aliases={'每日新闻', '新闻'}, block=True)
@daily.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 0:
        await universal_adapters.send_image(img_url, bot, event)
        await daily.finish()
    elif len(args) == 1:
        if args[0].lower() == 'subscribe' or args[0] == '订阅':
            if universal_adapters.is_onebot_v11(bot):
                bot_id = bot.self_id
                id = universal_adapters.get_group_id(event)
                data_cursor.execute(f'REPLACE INTO daily_subscribers (id, bot) VALUES ({id}, {bot_id})')
                await daily.finish('每日新闻订阅成功')
            else:
                await daily.finish('该功能仅支持 OneBot v11')
        elif args[0].lower() == 'unsubscribe' or args[0] == '退订':
            if universal_adapters.is_onebot_v11(bot):
                bot_id = bot.self_id
                id = universal_adapters.get_group_id(event)
                data_cursor.execute(f'DELETE FROM daily_subscribers WHERE id == {id} AND bot == {bot_id}')
                await daily.finish('每日新闻退订成功')
            else:
                await daily.finish('该功能仅支持 OneBot v11')
        else:
            await daily.finish('用法: ' + __plugin_meta__.usage)


@scheduler.scheduled_job("cron", hour="8", id="daily_news")
async def _():
    subscribers: list[list[int, int]] = data_cursor.execute('SELECT * FROM daily_subscribers').fetchall()
    for subscriber in subscribers:
        bot_id = subscriber[1]
        id = subscriber[0]
        try:
            bot = get_bot(str(bot_id))
            await bot.call_api('send_group_msg', group_id=id, message=f'[CQ:image,file={img_url}]')
        except KeyError:
            pass
