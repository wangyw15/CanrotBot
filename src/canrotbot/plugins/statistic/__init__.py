from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor, run_postprocessor
from nonebot_plugin_alconna import (
    MsgTarget,
)
from sqlalchemy import insert

from canrotbot.essentials.libraries import database

from .data import MessageHistory, PluginHistory


@event_preprocessor
async def _(target: MsgTarget, event: Event):
    try:
        with database.get_session().begin() as session:
            session.execute(
                insert(MessageHistory).values(
                    content=event.get_plaintext(),
                    private_chat=target.private,
                    channel_chat=target.channel,
                    self_id=target.self_id,
                    parent_id=target.parent_id,
                    target_id=target.id,
                    user_id=event.get_user_id(),
                )
            )
    except NotImplementedError:
        pass
    except ValueError:
        pass
    except Exception as e:
        raise e


@run_postprocessor
async def _(target: MsgTarget, event: Event, matcher: Matcher):
    try:
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
                    target_id=target.id,
                    user_id=event.get_user_id(),
                )
            )
    except NotImplementedError:
        pass
    except ValueError:
        pass
    except Exception as e:
        raise e
