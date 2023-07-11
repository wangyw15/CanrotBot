from datetime import datetime
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from adapters import unified
from essentials.libraries import user, economy, storage
from . import fortune

__plugin_meta__ = PluginMetadata(
    name='签到',
    description='每日签到，能够抽签和获得积分',
    usage='/<signin|签到|每日签到|抽签>',
    config=None
)

_signin_data = storage.PersistentData[dict[str, str]]('signin')

_signin_handler = on_shell_command('signin', aliases={'签到', '每日签到', '抽签'}, block=True)


@_signin_handler.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    # 查看所有主题
    if len(args) == 1 and args[0] in ['查看主题', 'listtheme', 'listthemes', 'list_theme', 'list_themes', 'themes']:
        await _signin_handler.finish('所有主题：\n\n' + '\n'.join(fortune.get_themes()))

    # 获取 uid
    puid = user.get_puid(bot, event)
    if not user.puid_user_exists(puid):
        await _signin_handler.finish('你还没有注册')
    uid = user.get_uid(puid)

    # 设置主题
    theme = 'random'
    if len(args) == 1:
        theme = args[0]

    # 判断是否签到过
    last_signin = _signin_data[uid]
    can_signin = False
    today = datetime.now().strftime('%Y-%m-%d')
    if not last_signin or 'last_date' not in last_signin:
        can_signin = True
    else:
        if not last_signin['last_date'] == today:
            can_signin = True

    # 构造消息
    final_msg = unified.Message()

    # 签到
    if can_signin:
        # 生成运势内容和对应图片
        img, title, content, rank = await fortune.generate_fortune(theme)
        _signin_data[uid] = {
            'last_date': today,
            'fortune_title': title,
            'fortune_content': content
        }
        with _signin_data.open(uid + '.png') as f:
            f.write(img)
        # 签到获得积分
        point_amount = 20 + rank
        economy.earn(uid, point_amount, "每日签到")

        final_msg += '签到成功！\n'
        final_msg += f'获得 {point_amount} 胡萝卜片\n'
        final_msg += '✨今日运势✨\n'
    else:
        final_msg += '你今天签过到了，再给你看一次哦🤗\n'

        title = _signin_data[uid]['fortune_title']
        content = _signin_data[uid]['fortune_content']
        if theme == 'random' and _signin_data.exists(uid + '.png'):
            with _signin_data.get_path(uid + '.png').open(mode='rb') as f:
                img: bytes = bytes(f.read())
        else:
            # 重新按内容生成图片
            img, _, _, _ = await fortune.generate_fortune(theme, title=title, content=content)
            with _signin_data.open(uid + '.png', mode='wb') as f:
                f.write(img)

    final_msg.append(unified.MessageSegment.image(img, f'运势: {title}\n详情: {content}'))
    await final_msg.send(bot, event)
    await _signin_handler.finish()
