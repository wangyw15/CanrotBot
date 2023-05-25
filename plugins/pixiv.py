from nonebot import on_regex
from nonebot.typing import T_State
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='Pixiv助手',
    description='提供一些有关 Pixiv 的功能',
    usage='链接会自动触发的，其他的还没想好',
    config=None
)

# TODO: 用正则匹配链接，然后调用pixiv api获取图片信息
