from nonebot_plugin_alconna import Target
from sqlalchemy import insert, select, update

from canrotbot.essentials.libraries import database

from .data import LLMSessionMode
from .model import SessionMode


def get_session_mode(target: Target) -> SessionMode:
    with database.get_session().begin() as session:
        mode = session.execute(
            select(LLMSessionMode).where(
                LLMSessionMode.private_chat == target.private,
                LLMSessionMode.channel_chat == target.channel,
                LLMSessionMode.self_id == target.self_id,
                LLMSessionMode.platform_id == target.id,
            )
        ).scalar_one_or_none()

        if mode is None:
            return SessionMode.temporary
        return mode.mode


def set_session_mode(target: Target, mode: SessionMode):
    with database.get_session().begin() as session:
        selected_mode = session.execute(
            select(LLMSessionMode).where(
                LLMSessionMode.private_chat == target.private,
                LLMSessionMode.channel_chat == target.channel,
                LLMSessionMode.self_id == target.self_id,
                LLMSessionMode.platform_id == target.id,
            )
        ).scalar_one_or_none()

        if selected_mode is None:
            session.execute(
                insert(LLMSessionMode).values(
                    private_chat=target.private,
                    channel_chat=target.channel,
                    self_id=target.self_id,
                    platform_id=target.id,
                    mode=mode,
                )
            )
        else:
            session.execute(
                update(LLMSessionMode)
                .where(
                    LLMSessionMode.private_chat == target.private,
                    LLMSessionMode.channel_chat == target.channel,
                    LLMSessionMode.self_id == target.self_id,
                    LLMSessionMode.platform_id == target.id,
                )
                .values(
                    mode=mode,
                )
            )
