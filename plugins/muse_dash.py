from nonebot import on_shell_command
from nonebot.adapters import MessageSegment, Bot, Event
from nonebot.params import CommandArg, ShellCommandArgv
from nonebot.plugin import PluginMetadata
from typing import Annotated
from ..libraries import muse_dash, user, universal_adapters
from ..libraries.config import get_config

__plugin_meta__ = PluginMetadata(
    name='MuseDash查分',
    description='从 https://musedash.moe/ 查询玩家数据',
    usage='/<md|muse-dash|muse_dash|喵斯|喵斯快跑> [功能]\n功能: \n<help|帮助>: 显示此帮助信息\n<bind|绑定> <玩家名|id>: 绑定 MuseDash.moe 账号\n<unbind|解绑>: 解绑 MuseDash.moe 账号\n<玩家名>: 查询玩家数据\n<me|我|我的|info|信息>\n/<md|muse-dash|muse_dash|喵斯|喵斯快跑>: 查询已绑定账号的数据',
    config=None
)

muse_dash.init_web_client(get_config('canrot_proxy'))


async def generate_muse_dash_message(player_id: str) -> list[str]:
    """生成消息"""
    if player_id:
        if data := await muse_dash.fetch_muse_dash_player_data(player_id):
            ret_msg = [f'玩家名：{data["name"]}\n' +
                       f'偏差值: {data["diff"]}\n' +
                       f'记录条数: {data["records"]}\n' +
                       f'完美数: {data["perfects"]}\n' +
                       f'平均准确率: {data["avg"]}%\n' +
                       f'上次更新: {data["last_update"]} 前\n']
            for song in data['songs']:
                ret_msg.append(f'[CQ:image,file={song["icon"]}]\n' +
                               f'曲目: {song["name"]} (Lv.{song["level"]})\n' +
                               f'作曲家: {song["musician"]}\n' +
                               f'准确度: {song["accuracy"]}%\n' +
                               f'得分: {song["score"]}\n' +
                               f'角色: {song["character"]}\n' +
                               f'精灵: {song["sprite"]}\n' +
                               f'总排名: {song["total_rank"]}\n'
                               )
            return ret_msg
    return []


_muse_dash = on_shell_command('muse-dash', aliases={'md', 'muse_dash', '喵斯', '喵斯快跑'}, block=True)


@_muse_dash.handle()
async def _(bot: Bot, event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    puid = universal_adapters.get_puid(bot, event)
    uid = user.get_uid(puid)
    if args:
        # 帮助信息
        if len(args) == 1 and (args[0].lower() == 'help' or args[0] == '帮助'):
            await _muse_dash.finish(__plugin_meta__.usage)
        # 处理命令
        if args[0].lower() == 'bind' or args[0] == '绑定':
            # 绑定账号
            if not uid:
                await _muse_dash.finish('你还未注册账号')
            player_name = args[1]
            # 获取玩家名和 ID
            player_id = ''
            if len(player_name) == 32:
                player_id = player_name
                player_name = (await muse_dash.fetch_muse_dash_player_data(player_id))['name']
            else:
                player_id = await muse_dash.search_muse_dash_player_id(player_name)
            if player_id and player_name:
                user.set_data_by_uid(uid, 'muse_dash_name', player_name)
                user.set_data_by_uid(uid, 'muse_dash_moe_id', player_id)
                await _muse_dash.send(f'绑定成功\n玩家名: {player_name}\nMuseDash.moe ID: {player_id}')
                ret_msg = await generate_muse_dash_message(player_id)
                await universal_adapters.send_group_forward_message(ret_msg, bot, event)
                await _muse_dash.finish()
            else:
                await _muse_dash.finish('绑定失败')
        elif args[0].lower() == 'unbind' or args[0] == '解绑':
            # 解绑账号
            if not uid:
                await _muse_dash.finish('你还未注册账号')
            user.set_data_by_uid(uid, 'muse_dash_name', '')
            user.set_data_by_uid(uid, 'muse_dash_moe_id', '')
            await _muse_dash.finish('解绑成功')
        elif args[0].lower() == 'me' or args[0] == '我' or args[0] == '我的' or args[0].lower() == 'info' or \
                args[0] == '信息':
            # 检查绑定信息
            if not uid:
                await _muse_dash.finish('你还未注册账号')
            player_name = user.get_data_by_uid(uid, 'muse_dash_name')
            player_id = user.get_data_by_uid(uid, 'muse_dash_moe_id')
            if player_id and player_name:
                await _muse_dash.finish(f'已绑定账号信息:\n玩家名: {player_name}\nMuseDash.moe ID: {player_id}')
            else:
                await _muse_dash.finish('您还没有绑定 MuseDash.moe 账号，请使用 /muse-dash help 查看帮助信息')
        elif len(args) == 1:
            # 获取玩家信息
            player_name = args[0]
            # 获取玩家 ID
            player_id = ''
            if len(player_name) == 32:
                player_id = player_name
            else:
                player_id = await muse_dash.search_muse_dash_player_id(player_name)
            # 生成消息
            if player_id:
                await _muse_dash.send('正在查分喵~')
                if universal_adapters.can_send_image(bot):
                    img = await muse_dash.generate_muse_dash_player_image(player_id)
                    await universal_adapters.send_image(img, bot, event)
                    await _muse_dash.finish()
                ret_msg = await generate_muse_dash_message(player_id)
                await universal_adapters.send_group_forward_message(ret_msg, bot, event)
                await _muse_dash.finish()
    else:
        if uid:
            if player_id := user.get_data_by_uid(uid, 'muse_dash_moe_id'):
                await _muse_dash.send('正在查分喵~')
                if universal_adapters.can_send_image(bot):
                    img = await muse_dash.generate_muse_dash_player_image(player_id)
                    await universal_adapters.send_image(img, bot, event)
                    await _muse_dash.finish()
                ret_msg = await generate_muse_dash_message(player_id)
                await universal_adapters.send_group_forward_message(ret_msg, bot, event)
                await _muse_dash.finish()
            else:
                await _muse_dash.finish('您还没有绑定 MuseDash.moe 账号，请使用 /muse-dash help 查看帮助信息')
        else:
            await _muse_dash.finish('你还未注册账号，请使用 /muse-dash help 查看帮助信息')
