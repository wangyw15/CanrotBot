import random

from nonebot import on_regex
from nonebot.plugin import PluginMetadata

from storage import asset

__plugin_meta__ = PluginMetadata(
    name="疯狂星期四",
    description="随机发送疯狂星期四文案",
    usage="疯狂星期[一|二|三|四|五|六|日|天]，也支持日文触发：狂乱[月|火|水|木|金|土|日]曜日",
    config=None,
)


crazy_thursday_posts: list[str] = asset.LocalAsset("crazy_thursday.json")["post"]
crazy_thursday_matcher = on_regex(
    r"疯狂星期[一二三四五六日天]|狂乱[月火水木金土日]曜日", block=True
)


@crazy_thursday_matcher.handle()
async def _():
    await crazy_thursday_matcher.finish(random.choice(crazy_thursday_posts))
