from datetime import datetime
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import Bot, Event, MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata
from sqlalchemy import select, insert

from adapters import unified
from essentials.libraries import user, economy
from storage import database, file
from . import data, fortune

__plugin_meta__ = PluginMetadata(
    name='签到',
    description='每日签到，能够抽签和获得积分',
    usage='/<signin|签到|每日签到|抽签>',
    config=None
)

_signin_files = file.FileStorage('signin')
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

    # 数据库 session
    session = database.get_session()()

    # 设置主题
    theme = 'random'
    if len(args) == 1:
        theme = args[0]

    # 判断是否签到过
    all_record = session.execute(select(data.SigninRecord).where(data.SigninRecord.user_id == uid)).scalars().all()
    today_record: data.SigninRecord | None = None
    for i in all_record:
        if i.time.date() == datetime.now().date():
            today_record = i
            break

    # 构造消息
    final_msg = unified.Message()

    # 签到
    if today_record is None:
        # 生成运势内容和对应图片
        img, title, content, rank = await fortune.generate_fortune(theme)
        session.execute(insert(data.SigninRecord).values(user_id=uid, time=datetime.now(), title=title, content=content))
        session.commit()
        with _signin_files(uid + '.png').open(mode='wb') as f:
            f.write(img)
        # 签到获得积分
        point_amount = 20 + rank
        economy.earn(uid, point_amount, "每日签到")

        final_msg += '签到成功！\n'
        final_msg += f'获得 {point_amount} 胡萝卜片\n'
        final_msg += '✨今日运势✨\n'
    else:
        final_msg += '你今天签过到了，再给你看一次哦🤗\n'

        title = today_record.title
        content = today_record.content

        if theme == 'random' and _signin_files(uid + '.png').exists():
            with _signin_files(uid + '.png').open(mode='rb') as f:
                img: bytes = bytes(f.read())
        else:
            # 重新按内容生成图片
            img, _, _, _ = await fortune.generate_fortune(theme, title=today_record.title, content=today_record.content)
            with _signin_files(uid + '.png').open(mode='wb') as f:
                f.write(img)

    final_msg.append(unified.MessageSegment.image(img, f'运势: {title}\n详情: {content}'))
    await final_msg.send()
    await _signin_handler.finish()
