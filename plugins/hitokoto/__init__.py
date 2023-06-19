import re
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from . import hitokoto

__plugin_meta__ = PluginMetadata(
    name='一言',
    description='随机一条一言',
    usage='/<hitokoto|一言> [一言分类，默认abc；或者uuid]\n分类详情查看发送 /一言 分类',
    config=None
)

_hitokoto = on_shell_command('hitokoto', aliases={'一言'}, block=True)
@_hitokoto.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    categories = 'abc'
    data: dict = {}
    if len(args) == 1:
        if args[0] in ['分类', 'category',  'categories']:
            ret_msg = []
            for category in hitokoto.get_categories():
                ret_msg.append(f'{category["key"]} - category["name"]')
                # ret_msg.append(f'名称: {category["name"]}\n描述: {category["desc"]}\n分类: {category["key"]}')
            await _hitokoto.finish('\n'.join(ret_msg))
        elif re.match(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', args[0]):
            data = hitokoto.get_hitokoto_by_uuid(args[0].strip())
        else:
            categories = args[0]
    if not data:
        data = hitokoto.random_hitokoto(categories)
    ret_msg = f'{data["hitokoto"]}\n-- {"" if not data["from_who"] else data["from_who"]}「{data["from"]}」\nhttps://hitokoto.cn/?uuid={data["uuid"]}'
    await _hitokoto.finish(ret_msg)
