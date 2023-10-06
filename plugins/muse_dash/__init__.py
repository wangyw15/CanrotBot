from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment, Bot, Event
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from adapters import unified
from essentials.libraries import user
from . import muse_dash, data
from storage import database
from sqlalchemy import select, insert, update, delete


__plugin_meta__ = PluginMetadata(
    name='MuseDash查分',
    description='从 https://musedash.moe/ 查询玩家数据',
    usage='/<md|muse-dash|muse_dash|喵斯|喵斯快跑> [功能]\n'
          '功能: \n'
          '<help|帮助>: 显示此帮助信息\n'
          '<bind|绑定> <玩家名|id>: 绑定 MuseDash.moe 账号\n'
          '<unbind|解绑>: 解绑 MuseDash.moe 账号\n'
          '<玩家名>: 查询玩家数据\n'
          '<me|我|我的|info|信息>\n'
          '/<md|muse-dash|muse_dash|喵斯|喵斯快跑>: 查询已绑定账号的数据',
    config=None
)

_muse_dash_handler = on_shell_command('muse-dash', aliases={'md', 'muse_dash', '喵斯', '喵斯快跑'}, block=True)


# TODO 改用 on_shell_command
@_muse_dash_handler.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    puid = user.get_puid(bot, event)
    uid = user.get_uid(puid)
    player_id = ''
    query = select(data.MuseDashAccount).where(data.MuseDashAccount.user_id == uid)
    if args:
        # 帮助信息
        if len(args) == 1 and args[0].lower() in ['help', '帮助']:
            await _muse_dash_handler.finish(__plugin_meta__.usage)
        # 处理命令
        if args[0].lower() in ['bind', '绑定']:
            # 绑定账号
            if not uid:
                await _muse_dash_handler.finish('你还未注册账号')
            player_name = args[1]
            # 获取玩家名和 ID
            if len(player_name) == 32:
                player_id = player_name
                player_name = (await muse_dash.fetch_muse_dash_player_data(player_id))['name']
            else:
                player_id = await muse_dash.search_muse_dash_player_id(player_name)
            if player_id and player_name:
                with database.get_session().begin() as session:
                    if session.execute(query).first() is not None:
                        session.execute(update(data.MuseDashAccount).
                                        where(data.MuseDashAccount.user_id == uid).
                                        values(player_name=player_name, player_id=player_id))
                    else:
                        session.execute(insert(data.MuseDashAccount).
                                        values(user_id=uid, player_name=player_name, player_id=player_id))
                    session.commit()
                await _muse_dash_handler.send(f'绑定成功\n玩家名: {player_name}\nMuseDash.moe ID: {player_id}')
            else:
                await _muse_dash_handler.finish('绑定失败')
        elif args[0].lower() in ['unbind', '解绑']:
            # 解绑账号
            if not uid:
                await _muse_dash_handler.finish('你还未注册账号')
            with database.get_session().begin() as session:
                session.execute(delete(data.MuseDashAccount).
                                where(data.MuseDashAccount.user_id == uid))
                session.commit()
            await _muse_dash_handler.finish('解绑成功')
        elif args[0].lower() in ['me', '我', '我的', 'info', '信息']:
            # 检查绑定信息
            if not uid:
                await _muse_dash_handler.finish('你还未注册账号')
            with database.get_session().begin() as session:
                account = session.execute(query).scalar_one_or_none()
            if account is not None:
                await _muse_dash_handler.finish(
                    f'已绑定账号信息:\n玩家名: {account.player_name}\nMuseDash.moe ID: {account.player_id}')
            else:
                await _muse_dash_handler.finish('您还没有绑定 MuseDash.moe 账号，请使用 /muse-dash help 查看帮助信息')
        elif len(args) == 1:
            # 获取玩家信息
            player_name = args[0]
            # 获取玩家 ID
            if len(player_name) == 32:
                player_id = player_name
            else:
                player_id = await muse_dash.search_muse_dash_player_id(player_name)
    else:
        # 检查绑定信息
        if not uid:
            await _muse_dash_handler.finish('你还未注册账号')
        with database.get_session().begin() as session:
            account = session.execute(query).scalar_one_or_none()
        if account is not None:
            player_id = account.player_id
    # 查分
    if player_id:
        await _muse_dash_handler.send('正在查分喵~')
        if unified.Detector.can_send_image(bot):
            img = await muse_dash.generate_muse_dash_player_image(player_id)
            await unified.MessageSegment.image(img).send()
        else:
            await _muse_dash_handler.send(await muse_dash.generate_muse_dash_message(player_id))
    await _muse_dash_handler.finish()
