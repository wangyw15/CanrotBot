from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    CommandMeta,
    Subcommand,
    on_alconna,
)
from sqlalchemy import insert

from canrotbot.essentials.libraries import database

from . import data, performace

cp_command = Alconna(
    "commercial_performance",
    Subcommand("pull", help_text="从网站上拉取演出信息"),
    Subcommand("list", help_text="列出已获取的演出信息"),
    meta=CommandMeta(description="从上海市文化和旅游局网站获取演出信息"),
)

__plugin_meta__ = PluginMetadata(
    name="演出",
    description=cp_command.meta.description,
    usage=cp_command.get_help(),
    config=None,
)

cp_matcher = on_alconna(
    cp_command,
    aliases={"演出"},
    block=True,
)


@cp_matcher.assign("pull")
async def _():
    ids: list[str] = []
    for i in range(1, 6):
        ids.extend(await performace.get_ids_by_page(i))

    for i in ids:
        current = await performace.get_data_by_id(i)
        if current:
            with database.get_session().begin() as session:
                session.execute(
                    insert(data.CommercialPerformance).values(current["performance"])
                )
                session.execute(
                    insert(data.PerformanceActors).values(current["actors"])
                )
    await cp_matcher.finish("拉取完成")


@cp_matcher.assign("list")
async def _():
    result = performace.list_performace(5)
    await cp_matcher.finish("\n".join([i.name for i in result]))
