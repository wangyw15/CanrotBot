import json
from typing import Sequence

from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy import delete, select, update

from canrotbot.essentials.libraries import database

from .data import LLMContext


def get_all_context(user_id: int = 0) -> Sequence[LLMContext]:
    """
    获取所有保存的上下文

    :param user_id: 用户id，默认所有用户

    :return: 保存的上下文
    """
    with database.get_session().begin() as session:
        if user_id:
            result = (
                session.execute(select(LLMContext).where(LLMContext.user_id == user_id))
                .scalars()
                .all()
            )
        else:
            result = session.execute(select(LLMContext)).scalars().all()
        session.expunge_all()
        return result


def create_context(
    owner_user_id: int,
    context: str | Sequence[ChatCompletionMessageParam] = "[]",
    name: str = "",
    selected: bool = True,
) -> int:
    """
    保存新上下文

    :param owner_user_id: 所有者user_id
    :param context: 上下文内容
    :param name: 上下文名称
    :param selected: 设置选中状态

    :return: 上下文id
    """
    with database.get_session().begin() as session:
        if isinstance(context, str):
            value = context
        else:
            value = json.dumps(context, ensure_ascii=False)

        context_item = LLMContext(
            user_id=owner_user_id, selected=False, context=value, name=name
        )
        session.add(context_item)
        session.flush()
        new_id = context_item.id

    if selected:
        select_context(new_id, owner_user_id)
    return new_id


def get_context(context_id: int, user_id: int = 0) -> LLMContext | None:
    """
    获取给定id的上下文

    :param context_id: 上下文id
    :param user_id: 用户id，若传入则作为查询条件

    :return: 获取到的上下文内容
    """
    with database.get_session().begin() as session:
        if user_id:
            result = session.execute(
                select(LLMContext)
                .where(LLMContext.id == context_id)
                .where(LLMContext.user_id == user_id)
            ).scalar_one_or_none()
        else:
            result = session.execute(
                select(LLMContext).where(LLMContext.id == context_id)
            ).scalar_one_or_none()
        return result


def get_selected_context(user_id: int) -> LLMContext | None:
    """
    获取给定用户所选定的上下文

    :param user_id: 用户id

    :return: 用户所选定的上下文内容
    """
    with database.get_session().begin() as session:
        result = session.execute(
            select(LLMContext)
            .where(LLMContext.user_id == user_id)
            .where(LLMContext.selected == True)
        ).scalar_one_or_none()
        session.expunge_all()
        return result


def update_context(
    context_id: int,
    new_context: str | Sequence[ChatCompletionMessageParam],
    name: str = "",
    user_id: int = 0,
) -> bool:
    """
    更新已有的上下文

    :param context_id: 上下文id
    :param new_context: 新上下文内容
    :param name: 上下文名称
    :param user_id: 用户id，若传入则作为查询条件

    :return: 更新是否成功
    """
    with database.get_session().begin() as session:
        if get_context(context_id, user_id) is None:
            return False

        if isinstance(new_context, str):
            value = new_context
        else:
            value = json.dumps(new_context, ensure_ascii=False)

        if name:
            session.execute(
                update(LLMContext)
                .where(LLMContext.id == context_id)
                .values(context=value, name=name)
            )
        else:
            session.execute(
                update(LLMContext)
                .where(LLMContext.id == context_id)
                .values(context=value)
            )
        return True


def update_selected_context(
    user_id: int,
    new_context: str | Sequence[ChatCompletionMessageParam],
    name: str = "",
) -> bool:
    """
    更新用户选定的上下文

    :param user_id: 用户id
    :param name: 上下文名称
    :param new_context: 新上下文内容

    :return: 更新是否成功
    """
    selected_context = get_selected_context(user_id)
    if selected_context is None:
        return False
    return update_context(selected_context.id, new_context, name, user_id)


def delete_context(context_id: int, user_id: int = 0) -> bool:
    """
    删除已有的上下文

    :param context_id: 上下文id
    :param user_id: 用户id，若传入则作为查询条件

    :return: 删除是否成功
    """
    with database.get_session().begin() as session:
        if get_context(context_id, user_id) is None:
            return False

        session.execute(delete(LLMContext).where(LLMContext.id == context_id))
        return True


def select_context(context_id: int, user_id: int) -> bool:
    """
    选择已有的上下文

    :param context_id: 要选中的上下文id
    :param user_id: 用户id

    :return: 选择是否成功
    """
    with database.get_session().begin() as session:
        if get_context(context_id, user_id) is None:
            return False

        session.execute(
            update(LLMContext)
            .where(LLMContext.user_id == user_id)
            .where(LLMContext.selected == True)
            .values(selected=False)
        )
        session.execute(
            update(LLMContext)
            .where(LLMContext.id == context_id)
            .where(LLMContext.user_id == user_id)
            .values(selected=True)
        )
        return True


__all__ = [
    "get_all_context",
    "create_context",
    "get_context",
    "get_selected_context",
    "update_context",
    "update_selected_context",
    "delete_context",
    "select_context",
]
