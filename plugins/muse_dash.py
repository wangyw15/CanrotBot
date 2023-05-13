from nonebot import on_command
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata

from ..libraries import muse_dash
from ..universal_adapters import send_group_forward_message
from ..data import get_config

__plugin_meta__ = PluginMetadata(
    name='MuseDash查分',
    description='从 https://musedash.moe/ 查询玩家数据',
    usage='/<md|muse-dash|muse_dash|喵斯|喵斯快跑> <玩家名>',
    config=None
)

muse_dash.init_web_client(get_config('canrot_proxy'))

_muse_dash = on_command('muse-dash', aliases={'md', 'muse_dash', '喵斯', '喵斯快跑'}, block=True)
@_muse_dash.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    if player_name := args.extract_plain_text():
        msg = []
        if player_id := await muse_dash.search_muse_dash_player_id(player_name):
            if data := await muse_dash.fetch_muse_dash_player_data(player_id):
                msg.append(f'玩家名：{data["name"]}\n' +
                    f'偏差值: {data["diff"]}\n' +
                    f'记录条数: {data["records"]}\n' +
                    f'完美数: {data["perfects"]}\n' +
                    f'平均准确率: {data["avg"]}%\n'
                )
                for song in data['songs']:
                    msg.append(f'[CQ:image,file={song["icon"]}]\n' +
                        f'曲目: {song["name"]} (Lv.{song["level"]})\n' +
                        f'作曲家: {song["musician"]}\n' +
                        f'准确度: {song["accuracy"]}%\n' +
                        f'得分: {song["score"]}\n' +
                        f'角色: {song["character"]}\n' +
                        f'精灵: {song["sprite"]}\n' +
                        f'总排名: {song["total_rank"]}\n'
                    )
                await send_group_forward_message(msg, bot, event)
                await _muse_dash.finish()
        await _muse_dash.finish('查询失败')
    else:
        await _muse_dash.finish('请输入玩家名')
