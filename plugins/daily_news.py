from typing import Annotated

from nonebot import on_shell_command, get_bot, require
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

from adapters import unified
from essentials.libraries import storage, util

__plugin_meta__ = PluginMetadata(
    name='看新闻',
    description='每日新闻，订阅功能仅支持 OneBot v11 的机器人',
    usage='/<daily|新闻|每日新闻>',
    config=None
)


_img_url = 'https://api.03c3.cn/zb/'
_subscribers = storage.PersistentList[dict[str, str]]('daily_subscribers')  # [{'bot': 'xxx', 'gid': 'xxx'}]


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
                _subscribers.append({'bot': bot_id, 'gid': gid})
                await daily.finish('每日新闻订阅成功')
            else:
                await daily.finish('该功能仅支持 OneBot v11')
        elif args[0].lower() == 'unsubscribe' or args[0] == '退订':
            if unified.Detector.is_onebot_v11(bot):
                bot_id = bot.self_id
                gid = util.get_group_id(event).split('_')[1]
                try:
                    _subscribers.remove({'bot': bot_id, 'gid': gid})
                    await daily.finish('每日新闻退订成功')
                except ValueError:
                    await daily.finish('每日新闻未订阅')
            else:
                await daily.finish('该功能仅支持 OneBot v11')
        else:
            await daily.finish('用法: ' + __plugin_meta__.usage)


@scheduler.scheduled_job("cron", hour="10", id="daily_news")
async def _():
    for subscriber in _subscribers:
        bot_id = subscriber['bot']
        gid = subscriber['gid']
        try:
            bot = get_bot(str(bot_id))
            await bot.call_api('send_group_msg', group_id=gid, message=f'[CQ:image,file={_img_url}]')
        except KeyError:
            pass
