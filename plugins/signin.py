import base64
from datetime import datetime

from nonebot import on_command
from nonebot.adapters import Bot, Event, Message
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from ..libraries import fortune, user, economy
from ..adapters import unified

__plugin_meta__ = PluginMetadata(
    name='签到',
    description='每日签到，能够抽签和获得积分',
    usage='/<signin|签到|每日签到|抽签>',
    config=None
)

_signin_handler = on_command('signin', aliases={'签到', '每日签到', '抽签'}, block=True)
@_signin_handler.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    puid = unified.get_puid(bot, event)
    if not user.puid_user_exists(puid):
        await _signin_handler.finish('你还没有注册')
    
    # theme
    theme = 'random'
    if msg := args.extract_plain_text():
        theme = msg
    
    # get uid
    uid = user.get_uid(puid)

    # determine if the user can sign in
    last_signin = user.get_data_by_uid(uid, 'signin_date')
    can_signin = False
    if not last_signin:
        can_signin = True
    today = datetime.now().strftime('%Y-%m-%d')
    if not last_signin == today:
        can_signin = True

    final_msg = unified.Message()

    # signin
    if can_signin:
        # fortune
        theme = fortune.get_theme_key_from_name(theme)
        img, title, content, rank = await fortune.generate_fortune(theme)
        user.set_data_by_uid(uid, 'signin_date', today)
        user.set_data_by_uid(uid, 'signin_fortune_image', img)
        user.set_data_by_uid(uid, 'signin_fortune_title', title)
        user.set_data_by_uid(uid, 'signin_fortune_content', content)
        # gain points
        point_amount = 20 + rank
        economy.earn(uid, point_amount)

        final_msg += '签到成功！\n'
        final_msg += f'获得 {point_amount} 胡萝卜片\n'
        final_msg += '✨今日运势✨\n'
    else:
        img = user.get_data_by_uid(uid, 'signin_fortune_image')
        final_msg += '你今天签过到了，再给你看一次哦🤗\n'
        title = user.get_data_by_uid(uid, 'signin_fortune_title')
        content = user.get_data_by_uid(uid, 'signin_fortune_content')

    final_msg.append(unified.MessageSegment.image(base64.b64decode(img), f'运势: {title}\n详情: {content}'))
    await final_msg.send(bot, event)
    await _signin_handler.finish()
