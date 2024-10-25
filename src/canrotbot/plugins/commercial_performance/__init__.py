from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata
from sqlalchemy import select, insert, cast, Integer

from canrotbot.essentials.libraries import database
from . import data, scraper

__plugin_meta__ = PluginMetadata(
    name="演出",
    description="从上海市文化和旅游局网站获取演出信息",
    usage="懒得写",
    config=None,  # TODO 帮助信息
)


_commercial_performance_handler = on_shell_command(
    "commercial_performance", aliases={"演出"}, block=True
)


@_commercial_performance_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 1:
        if args[0].lower() in ["pull"]:
            ids: list[str] = []
            for i in range(1, 11):
                ids.extend(await scraper.get_ids_by_page(i))
            for i in ids:
                current = await scraper.get_data_by_id(i)
                with database.get_session().begin() as session:
                    session.execute(
                        insert(data.CommercialPerformance).values(
                            current["performance"]
                        )
                    )
                    session.execute(
                        insert(data.PerformanceActors).values(current["actors"])
                    )
            await _commercial_performance_handler.finish("拉取完成")
        elif args[0].lower() in ["get"]:
            with database.get_session().begin() as session:
                ret = (
                    session.execute(
                        select(data.CommercialPerformance)
                        .order_by(
                            cast(data.CommercialPerformance.acceptance_id, Integer)
                        )
                        .limit(5)
                    )
                    .scalars()
                    .all()
                )
                await _commercial_performance_handler.finish(
                    "\n".join([i.name for i in ret])
                )
