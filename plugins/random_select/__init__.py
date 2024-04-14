import random
from collections import namedtuple

from arclet.alconna import Alconna, Args
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Match,
)

__plugin_meta__ = PluginMetadata(
    name="随机选择",
    description="多个选项里随机选一个，可以设置权重",
    usage="/<random|r|随机> <项目>",
    config=None,
)

_command = on_alconna(
    Alconna(
        "random",
        Args["items", str],
    )
)

Item = namedtuple("Item", ["name", "weight"])


@_command.handle()
async def _(items: Match[str]):
    if items.available:
        _command.set_path_arg("items", items.result)


@_command.got_path("items", prompt="请输入项目")
async def _(items: str):
    raw_items = items.replace("，", ",").split(",")
    items: list[Item] = []

    # 处理权重
    for raw_item in raw_items:
        raw_item = raw_item.strip()
        if not raw_item:
            continue

        raw_item = raw_item.replace("：", ":")
        weight = 1
        if ":" in raw_item:
            raw_item, weight = raw_item.split(":", 1)
            weight = float(weight)
        items.append(Item(raw_item, weight))

    # 计算权重总和
    total_weight = sum(item.weight for item in items)

    # 随机选择
    random_num = random.uniform(0, total_weight)
    for item in items:
        random_num -= item.weight
        if random_num <= 0:
            break
    else:
        raise FinishedException("随机选择失败")

    await _command.finish(f"选择了：{item.name}")
