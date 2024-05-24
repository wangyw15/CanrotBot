from arclet.alconna import Alconna, Args, Option
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    AlconnaQuery,
    Query,
)
from sqlalchemy import select, insert, delete

from storage import database
from . import data, random_selector

__plugin_meta__ = PluginMetadata(
    name="随机选择",
    description="多个选项里随机选一个，可以设置权重",
    usage="/<random|r|随机|随机选择> <项目|添加预设|列出预设|查看预设|删除预设>",
    config=None,
)


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
        Args["items", str, ""],
    ),
    aliases={"r", "随机", "随机选择"},
)


@_command.assign("add-preset")
async def _(
    name: Query[str] = AlconnaQuery("name"),
    preset_items: Query[str] = AlconnaQuery("preset_items"),
):
    raw_items = preset_items.result.strip()

    from nonebot.log import logger

    logger.info(f"name: {name.result}")
    logger.info(f"raw_items: {preset_items.result}")

    if not raw_items:
        await _command.finish("请提供项目")

    items = random_selector.parse_items(raw_items)
    with database.get_session().begin() as session:
        session.execute(
            insert(data.RandomSelectPreset).values(
                name=name.result.strip(), items=random_selector.dump_items(items)
            )
        )
    await _command.finish(f"添加预设 {name.result.strip()} 成功")


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
                data.RandomSelectPreset.name == name.result.strip()
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
                data.RandomSelectPreset.name == name.result.strip()
            )
        )
    await _command.finish(f"删除预设 {name.result.strip()} 成功")


@_command.handle()
async def _(items: Query[str] = AlconnaQuery("items", "")):
    raw_items = items.result.strip()

    if not raw_items:
        await _command.finish(__plugin_meta__.usage)

    parsed_items = random_selector.parse_items(raw_items)
    preset_prompt = ""

    if len(parsed_items) == 1:
        with database.get_session().begin() as session:
            result: str | None = session.execute(
                select(data.RandomSelectPreset.items).where(
                    data.RandomSelectPreset.name == raw_items
                )
            ).scalar_one_or_none()
            if result:
                preset_prompt = "使用预设项目：" + raw_items
                parsed_items = random_selector.parse_items(result)

    await _command.finish(
        (
            preset_prompt
            + "\n选择了："
            + random_selector.random_select_from_list(parsed_items)
        ).strip()
    )
