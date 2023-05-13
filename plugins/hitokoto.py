from nonebot import on_command
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
import re

from ..libraries import hitokoto, universal_adapters

__plugin_meta__ = PluginMetadata(
    name='一言',
    description='随机一条一言',
    usage='/<hitokoto|一言> [一言分类，默认abc；或者uuid]\n分类详情查看发送 /一言 分类',
    config=None
)

_hitokoto = on_command('hitokoto', aliases={'一言'}, block=True)
@_hitokoto.handle()
async def _(bot: Bot, event: Event, args: Message = CommandArg()):
    categories = 'abc'
    data: dict = {}
    if msg := args.extract_plain_text():
        if msg == '分类' or msg == 'category' or msg == 'categories':
            ret_msg = []
            for category in hitokoto.get_categories():
                ret_msg.append(f'名称: {category["name"]}\n描述: {category["desc"]}\n分类: {category["key"]}')
            await universal_adapters.send_group_forward_message(ret_msg, bot, event, header='一言分类:')
            await _hitokoto.finish()
        elif re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', msg):
            data = hitokoto.get_hitokoto_by_uuid(msg.strip())
        elif ' ' in msg:
            categories = ''.join([x.strip() for x in msg.split()])
        elif ',' in msg:
            categories = ''.join([x.strip() for x in msg.split(',')])
        else:
            categories = msg
    if not data:
        data = hitokoto.random_hitokoto(categories)
    ret_msg = f'{data["hitokoto"]}\n-- {"" if not data["from_who"] else data["from_who"]}「{data["from"]}」\nhttps://hitokoto.cn/?uuid={data["uuid"]}'
    await _hitokoto.finish(ret_msg)
