from datetime import datetime

from arclet.alconna import Option, Args
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    AlconnaQuery,
    Query,
    UniMessage,
    Text,
    Image,
)
from sqlalchemy import select, insert

from essentials.libraries import user, economy, util, path, database
from . import data, fortune

__plugin_meta__ = PluginMetadata(
    name="签到",
    description="每日签到，能够抽签和获得积分",
    usage="/<signin|签到|每日签到|抽签>",
    config=None,
)

DATA_PATH = path.get_data_path("signin")

_command = on_alconna(
    Alconna(
        "signin",
        Option(
            "themes",
            alias=[
                "查看主题",
                "listtheme",
                "listthemes",
                "list_theme",
                "list_themes",
                "themes",
            ],
        ),
        Args["theme", str, "random"],
    ),
    aliases={"签到"},
    block=True,
)


@_command.assign("themes")
async def _():
    await _command.finish("所有主题：\n\n" + "\n".join(fortune.get_themes()))


@_command.handle()
async def _(event: Event, theme: Query[str] = AlconnaQuery("theme", "random")):
    theme = theme.result.strip().lower()

    # 获取 uid
    puid = event.get_user_id()
    if not user.puid_user_exists(puid):
        await _command.finish("你还没有注册")
    uid = user.get_uid(puid)

    # 数据库 session
    session = database.get_session()()

    # 判断是否签到过
    all_record = (
        session.execute(
            select(data.SigninRecord).where(data.SigninRecord.user_id.is_(uid))
        )
        .scalars()
        .all()
    )
    today_record: data.SigninRecord | None = None
    for i in all_record:
        if i.time.date() == datetime.now().date():
            today_record = i
            break

    # 构造消息
    final_msg = UniMessage()

    # 签到
    if today_record is None:
        # 生成运势内容和对应图片
        img, title, content, rank = await fortune.generate_fortune(theme)
        session.execute(
            insert(data.SigninRecord).values(
                user_id=uid, time=datetime.now(), title=title, content=content
            )
        )
        session.commit()
        with (DATA_PATH / f"{uid}.png").open(mode="wb") as f:
            f.write(img)
        # 签到获得积分
        point_amount = 20 + rank
        economy.earn(uid, point_amount, "每日签到")

        final_msg += Text(
            "签到成功！\n" f"获得 {point_amount} 胡萝卜片\n" "✨今日运势✨\n"
        )
    else:
        final_msg += Text("你今天签过到了，再给你看一次哦🤗\n")

        title = today_record.title
        content = today_record.content

        if theme == "random" and (DATA_PATH / f"{uid}.png").exists():
            img: bytes = (DATA_PATH / f"{uid}.png").read_bytes()
        else:
            # 重新按内容生成图片
            img, _, _, _ = await fortune.generate_fortune(
                theme, title=today_record.title, content=today_record.content
            )
            with (DATA_PATH / f"{uid}.png").open(mode="wb") as f:
                f.write(img)
    if await util.can_send_segment(Image):
        final_msg.append(Image(raw=img))
    else:
        final_msg += Text(f"运势: {title}\n详情: {content}")
    await _command.finish(final_msg)
