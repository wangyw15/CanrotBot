from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import Event, MessageSegment
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata
from sqlalchemy import select, update, insert

from essentials.libraries import util
from storage import database
from . import data

__plugin_meta__ = PluginMetadata(
    name="机器人管理工具", description="可以在群内禁用机器人", usage="待定", config=None
)


_bot_admin_handler = on_shell_command("admin", aliases={"管理"}, block=True)


@_bot_admin_handler.handle()
async def _(
    event: Event, args: Annotated[list[str | MessageSegment], ShellCommandArgv()]
):
    if gid := util.get_group_id(event):
        enable = True
        if len(args) == 1 and args[0].lower() in ["enable", "启用"]:
            enable = True
        elif len(args) == 1 and args[0].lower() in ["disable", "禁用"]:
            enable = False

        query = select(data.GroupConfig).where(data.GroupConfig.group_id == gid)  # type: ignore
        with database.get_session().begin() as session:
            # 自动创建群组配置
            if session.execute(query).first() is None:
                session.execute(insert(data.GroupConfig).values(group_id=gid))
            # 设置启用状态
            if enable:
                session.execute(
                    update(data.GroupConfig)
                    .where(data.GroupConfig.group_id == gid)  # type: ignore
                    .values(enable_bot=True)
                )
            else:
                session.execute(
                    update(data.GroupConfig)
                    .where(data.GroupConfig.group_id == gid)  # type: ignore
                    .values(enable_bot=False)
                )
            session.commit()
        await _bot_admin_handler.finish(f'已{"启" if enable else "禁"}用')
    else:
        await _bot_admin_handler.finish("仅限在群聊使用")


@run_preprocessor
async def _(event: Event, matcher: Matcher):
    if matcher.module.__name__ == __name__:
        return
    if gid := util.get_group_id(event):
        query = select(data.GroupConfig).where(data.GroupConfig.group_id == gid)  # type: ignore
        with database.get_session().begin() as session:
            config = session.execute(query).scalar_one_or_none()
            if (config is not None) and (not config.enable_bot):
                await matcher.finish()
