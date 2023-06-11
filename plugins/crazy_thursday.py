import json
import random
from pathlib import Path

from nonebot import logger, on_regex
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='疯狂星期四',
    description='随机发送疯狂星期四文案',
    usage='疯狂星期[一|二|三|四|五|六|日|天]，也支持日文触发：狂乱[月|火|水|木|金|土|日]曜日',
    config=None
)

_crazy_thursday_posts: list[str] = []


def _load_crazy_thursday_data() -> None:
    global _crazy_thursday_posts
    with (Path(__file__).parent.parent / 'assets' / 'crazy_thursday.json').open('r', encoding='utf-8') as f:
        data = json.load(f)
        _crazy_thursday_posts = data['post']
        logger.info('Crazy thursday data version: ' + str(data['version']))
        logger.info('Crazy thursday posts: ' + str(len(_crazy_thursday_posts)))


_load_crazy_thursday_data()


_crazy_thursday_handler = on_regex(r'疯狂星期[一二三四五六日天]|狂乱[月火水木金土日]曜日', block=True)
@_crazy_thursday_handler.handle()
async def _():
    await _crazy_thursday_handler.finish(random.choice(_crazy_thursday_posts))
