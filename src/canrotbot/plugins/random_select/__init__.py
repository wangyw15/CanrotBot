from typing import cast

from arclet.alconna import Alconna, Args, Option
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    AlconnaQuery,
    Query,
)
from sqlalchemy import select, insert, delete, ColumnElement

from canrotbot.essentials.libraries import database
from . import data, random_selector

__plugin_meta__ = PluginMetadata(
    name="随机选择",
    description="多个选项里随机选一个，可以设置权重",
    usage="/<random|r|随机|随机选择> <项目|添加预设|列出预设|查看预设|删除预设>",
    config=None,
)

EMPTY_PROMPT = "{EMPTY_PROMPT}"

_command = on_alconna(
    Alconna(
        "random",
        Option(
            "add-preset",
            Args["name", str]["preset_items", str],
            alias=["添加预设"],
        ),
        Option(
            "list-preset",
            alias=["列出预设"],
        ),
        Option(
            "view-preset",
            Args["name", str],
            alias=["查看预设"],
        ),
        Option(
            "delete-preset",
            Args["name", str],
            alias=["删除预设"],
        ),
        Args["items", str, ""]["prompt", str, ""],
    ),
    aliases={"r", "随机", "随机选择"},
)

# 抛硬币
_command.shortcut(
    "coin",
    {"args": ["正面,反面", EMPTY_PROMPT], "prefix": True},
)


@_command.assign("add-preset")
async def _(
    name: Query[str] = AlconnaQuery("name"),
    preset_items: Query[str] = AlconnaQuery("preset_items"),
):
    preset_name = name.result.strip()
    raw_items = preset_items.result.strip()

    if not raw_items:
        await _command.finish("请提供项目")

    items = random_selector.parse_items(raw_items)
    with database.get_session().begin() as session:
        result = session.execute(
            select(data.RandomSelectPreset).where(
                cast(ColumnElement[bool], data.RandomSelectPreset.name == preset_name)
            )
        ).scalar_one_or_none()
        if result:
            await _command.finish(f"预设 {preset_name} 已存在")

        session.execute(
            insert(data.RandomSelectPreset).values(
                name=preset_name, items=random_selector.dump_items(items)
            )
        )
    await _command.finish(f"添加预设 {preset_name} 成功")


@_command.assign("list-preset")
async def _():
    with database.get_session().begin() as session:
        result = session.execute(select(data.RandomSelectPreset.name)).scalars().all()
        if not result:
            await _command.finish("没有预设")
        await _command.finish(
            "随机预设：\n" + "\n".join(f"{preset_name}" for preset_name in result)
        )


@_command.assign("view-preset")
async def _(name: Query[str] = AlconnaQuery("name")):
    with database.get_session().begin() as session:
        result: str | None = session.execute(
            select(data.RandomSelectPreset.items).where(
                cast(
                    ColumnElement[bool],
                    data.RandomSelectPreset.name == name.result.strip(),
                )
            )
        ).scalar_one_or_none()
        if not result:
            await _command.finish("预设不存在")
        await _command.finish(f"预设 {name.result.strip()}：\n{result}")


@_command.assign("delete-preset")
async def _(name: Query[str] = AlconnaQuery("name")):
    with database.get_session().begin() as session:
        session.execute(
            delete(data.RandomSelectPreset).where(
                cast(
                    ColumnElement[bool],
                    data.RandomSelectPreset.name == name.result.strip(),
                )
            )
        )
    await _command.finish(f"删除预设 {name.result.strip()} 成功")


@_command.handle()
async def _(
    items: Query[str] = AlconnaQuery("items", ""),
    prompt: Query[str] = AlconnaQuery("prompt", ""),
):
    raw_items = items.result.strip()
    custom_prompt = prompt.result

    if not raw_items:
        await _command.finish(__plugin_meta__.usage)

    parsed_items = random_selector.parse_items(raw_items)
    preset_prompt = ""

    if len(parsed_items) == 1:
        with database.get_session().begin() as session:
            result: str | None = session.execute(
                select(data.RandomSelectPreset.items).where(
                    cast(ColumnElement[bool], data.RandomSelectPreset.name == raw_items)
                )
            ).scalar_one_or_none()
            if result:
                preset_prompt = "使用预设项目：" + raw_items + "\n"
                parsed_items = random_selector.parse_items(result)

    prompt = preset_prompt + "选择了："

    if custom_prompt == EMPTY_PROMPT:
        prompt = ""
    elif custom_prompt:
        prompt = custom_prompt

    await _command.finish(
        (
            prompt + " ".join(random_selector.random_select_from_list(parsed_items))
        ).strip()
    )
