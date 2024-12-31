from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor, run_postprocessor
from nonebot_plugin_alconna import (
    UniMessage,
)
from sqlalchemy import insert

from canrotbot.essentials.libraries import database

from .data import MessageHistory, PluginHistory


@event_preprocessor
async def _(bot: Bot, event: Event):
    try:
        target = UniMessage.get_target(event, bot)
        with database.get_session().begin() as session:
            session.execute(
                insert(MessageHistory).values(
                    content=event.get_plaintext(),
                    private_chat=target.private,
                    channel_chat=target.channel,
                    self_id=target.self_id,
                    parent_id=target.parent_id,
                    platform_id=target.id,
                )
            )
    except NotImplementedError:
        pass
    except Exception as e:
        raise e


@run_postprocessor
async def _(bot: Bot, event: Event, matcher: Matcher):
    try:
        target = UniMessage.get_target(event, bot)
        with database.get_session().begin() as session:
            session.execute(
                insert(PluginHistory).values(
                    plugin_name=matcher.plugin_name,
                    module_name=matcher.module_name,
                    command=event.get_plaintext(),
                    private_chat=target.private,
                    channel_chat=target.channel,
                    self_id=target.self_id,
                    parent_id=target.parent_id,
                    platform_id=target.id,
                )
            )
    except NotImplementedError:
        pass
    except Exception as e:
        raise e
