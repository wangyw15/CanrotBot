import json
import random
from collections import namedtuple
from typing import Annotated

from canrotbot.libraries.llm.tool import BaseTool

Item = namedtuple("Item", ["name", "weight"])


def parse_items(raw_items: str) -> list[list[Item]]:
    """
    解析项目列表

    :param raw_items: 项目列表，同一个列表中的项目以逗号分隔，不同列表以分号分割

    :return: 项目列表
    """
    raw_items_set = raw_items.replace("；", ";").split(";")
    result: list[list[Item]] = []

    # 处理权重
    for raw_items in raw_items_set:
        current_raw_items = raw_items.replace("，", ",").split(",")
        current_items: list[Item] = []
        for raw_item in current_raw_items:
            raw_item = raw_item.strip()
            if not raw_item:
                continue

            raw_item = raw_item.replace("：", ":")
            weight = 1
            if ":" in raw_item:
                raw_item, weight = raw_item.split(":", 1)
                weight = float(weight)
            current_items.append(Item(raw_item, weight))
        result.append(current_items)

    return result


def dump_items(items_set: list[list[Item]]) -> str:
    """
    将项目列表转换为字符串

    :param items_set: 项目列表

    :return: 字符串
    """
    return ";".join(
        (",".join(f"{item.name}:{item.weight}" for item in items))
        for items in items_set
    )


def random_select_from_list(items_set: list[list[Item]]) -> list[str]:
    """
    从多个列表中，对每一个列表随机选择一个项目

    :param items_set: 项目列表

    :return: 选择的项目
    """
    if not items_set:
        raise ValueError("Empty items set")
    for items in items_set:
        if not items:
            raise ValueError("Empty items")

    selected_items: list[str] = []

    for items in items_set:
        # 计算权重总和
        total_weight = sum(item.weight for item in items)

        if total_weight == 0:
            raise ValueError("Total weight is 0")

        # 随机选择
        random_num = random.uniform(0, total_weight)
        for item in items:
            random_num -= item.weight
            if random_num <= 0:
                break
        else:
            raise ValueError("Random select failed")
        selected_items.append(item.name)

    return selected_items


class RandomSelectTool(BaseTool):
    __tool_name__ = "random_select"
    __description__ = "在多个列表中，对每一个列表随机选择一个项目；同一个列表中的项目以逗号分隔，不同列表以分号分割"
    __command__ = False

    async def __call__(
        self,
        raw_items: Annotated[
            str, "项目列表，同一个列表中的项目以逗号分隔，不同列表以分号分割"
        ],
    ) -> str:
        items = parse_items(raw_items)
        self.items = items
        return json.dumps(
            {"selected": random_select_from_list(items)}, ensure_ascii=False
        )
