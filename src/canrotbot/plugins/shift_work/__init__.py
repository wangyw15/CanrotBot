import ast
from datetime import datetime

from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Query,
    Subcommand,
    on_alconna,
)

from canrotbot.essentials.libraries.util import get_file_message

from . import calendar, util

shift_work_command = Alconna(
    "shift_work",
    Subcommand(
        "calendar",
        Args["calendar_cycle", str],
        Args["calendar_start", str],
        Args["calendar_end", str],
        alias=["日历"],
        help_text="生成倒班日历\n用例:"
        + '/shift_work calendar [("白班","08:00","20:00"),("夜班","20:00","08:00"),None,None] 20251001 20251231',
    ),
    meta=CommandMeta("根据规则生成倒班日历"),
)

__plugin_meta__ = PluginMetadata(
    "倒班日历",
    description=shift_work_command.meta.description,
    usage=shift_work_command.get_help(),
)

shift_work_matcher = on_alconna(
    shift_work_command,
    aliases={"倒班"},
    block=True,
)


@shift_work_matcher.assign("calendar")
async def _(
    calendar_cycle: Query[str] = Query("calendar_cycle"),
    calendar_start: Query[str] = Query("calendar_start"),
    calendar_end: Query[str] = Query("calendar_end"),
):
    if not (
        calendar_cycle.available and calendar_start.available and calendar_end.available
    ):
        await shift_work_matcher.finish("缺少必要参数")

    raw_cycles: list[tuple[str, str, str] | list[str] | None] = ast.literal_eval(
        calendar_cycle.result
    )
    parsed_cycles = util.parse_cycles(raw_cycles)
    start_date = util.parse_date(calendar_start.result)
    end_date = util.parse_date(calendar_end.result)

    if start_date is None:
        await shift_work_matcher.finish(f"无法解析起始日期: {calendar_start.result}")
    if end_date is None:
        await shift_work_matcher.finish(f"无法解析结束日期: {calendar_end.result}")

    filename = datetime.now().strftime("%Y%m%dT%H%M%S") + ".ics"
    content = calendar.generate_calendar(parsed_cycles, start_date, end_date).to_ical()

    await shift_work_matcher.finish(await get_file_message(filename, content))
