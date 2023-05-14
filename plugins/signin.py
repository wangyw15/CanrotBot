from nonebot import on_command
from nonebot.adapters import Bot, Event, Message
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata
from datetime import datetime
import random

from ..libraries import universal_adapters, fortune, user, economy

__plugin_meta__ = PluginMetadata(
    name='签到',
    description='每日签到，能够抽签和获得积分',
    usage='/<signin|签到|每日签到|抽签>',
    config=None
)

_signin_handler = on_command('signin', aliases={'签到', '每日签到', '抽签'}, block=True)
@_signin_handler.handle()
async def _(state: T_State, bot: Bot, event: Event, args: Message = CommandArg()):
    puid = universal_adapters.get_puid(bot, event)
    if not user.puid_user_exists(puid):
        await _signin_handler.finish('你还没有注册')
    
    # theme
    theme = 'random'
    if msg := args.extract_plain_text():
        theme = msg
    
    # get uid
    uid = user.get_uid(puid)

    # determine if the user can signin
    last_signin = user.get_data(uid, 'signin_date')
    can_signin = False
    if not last_signin:
        can_signin = True
    today = datetime.now().strftime('%Y-%m-%d')
    if not last_signin == today:
        can_signin = True
    
    # signin
    if can_signin:
        # fortune
        img, title, content, rank = fortune.generate_fortune(theme)
        user.set_data(uid, 'signin_date', today)
        user.set_data(uid, 'signin_fortune_image', img)
        user.set_data(uid, 'signin_fortune_title', title)
        user.set_data(uid, 'signin_fortune_content', content)
        # gain points
        point_amount = 20 + rank
        economy.earn(uid, point_amount)

        msg = '签到成功！\n'
        msg += f'获得 {point_amount} 胡萝卜片\n'
        msg += '✨今日运势✨\n'
        if universal_adapters.is_onebot_v11(bot) or universal_adapters.is_onebot_v12(bot):
            msg += f'[CQ:image,file=base64://{img}]\n'
        else:
            msg += f'运势: {title}\n详情: {content}\n'
        await _signin_handler.finish(msg)
    else:
        await _signin_handler.finish('你今天签过到了，再给你看一次哦🤗')
