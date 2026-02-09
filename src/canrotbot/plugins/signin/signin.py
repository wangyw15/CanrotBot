from datetime import datetime
from typing import cast

from nonebot_plugin_alconna import Image, Text, UniMessage
from sqlalchemy import ColumnElement, insert, select

from canrotbot.essentials.libraries import database, path, user, util
from canrotbot.llm.tools import register_tool

from . import data, fortune

DATA_PATH = path.get_data_path("signin")


def get_today_record(user_id: int) -> data.SigninRecord | None:
    """
    获取给定用户的当天签到记录

    Args:
        user_id: 说明
    Returns:
        当前的签到记录，若未签到或用户不存在则返回None
    """
    with database.get_session().begin() as session:
        all_record = (
            session.execute(
                select(data.SigninRecord).where(
                    cast(ColumnElement[bool], data.SigninRecord.user_id == user_id)
                )
            )
            .scalars()
            .all()
        )
        for i in all_record:
            if i.time.date() == datetime.now().date():
                session.expunge(i)
                return i
    return None


def set_today_record(user_id: int, title: str, content: str):
    """
    设置给定用户的当天签到记录

    Args:
        user_id: 说明
        title: 运势类型
        content: 运势内容
    """
    with database.get_session().begin() as session:
        session.execute(
            insert(data.SigninRecord).values(
                user_id=user_id, time=datetime.now(), title=title, content=content
            )
        )


async def generate_message(
    title: str,
    content: str,
    already_signin: bool,
    image: bytes | None = None,
):
    """
    生成运势消息

    Args:
        title: 运势类型
        content: 运势内容
        already_signin: 当日是否已经签到
        image: 运势图

    Returns:
        生成的消息
    """
    msg = UniMessage()

    if already_signin:
        msg += Text("你今天签过到了，再给你看一次哦🤗\n")
    else:
        msg += Text("签到成功！\n")

    if image is not None and await util.can_send_segment(Image):
        msg += Image(raw=image)
    else:
        msg += Text(f"运势: {title}\n{content}")

    return msg


@register_tool()
async def signin(theme: str = "random") -> dict[str, str | bool]:
    """
    进行每日签到，调用后tool会自动向用户发送一张运势图片（若支持），并且返回运势数据。若用户进行了重复签到，则不会生成新的运势文字内容；若指定了random之外的主题，会重新生成运势图片，但是文字内容不变。

    Args:
        theme: 运势图片的主题，默认为random，为随机主题

    Returns:
        返回运势数据，包含类型和内容和用户是否在当日已经签到过后进行重复签到
    """
    user_id = user.get_uid()
    today_record = get_today_record(user_id)

    if today_record is None:
        title, content = fortune.get_random_copywrite()
        set_today_record(user_id, title, content)
    else:
        title = today_record.title
        content = today_record.content

    if await util.can_send_segment(Image):
        if (
            today_record is not None
            and theme == "random"
            and (DATA_PATH / f"{user_id}.png").exists()
        ):
            image = (DATA_PATH / f"{user_id}.png").read_bytes()
        else:
            image = await fortune.generate_image(title, content, theme)
            with (DATA_PATH / f"{user_id}.png").open("wb") as f:
                f.write(image)
        await UniMessage.image(raw=image).send()

    return {
        "type": title,
        "content": content,
        "repeat_signin": today_record is not None,
    }
