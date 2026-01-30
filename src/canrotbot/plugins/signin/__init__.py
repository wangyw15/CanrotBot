from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Image,
    Query,
    Subcommand,
    on_alconna,
)

from canrotbot.essentials.libraries import path, user, util

from . import fortune, signin

singin_command = Alconna(
    "signin",
    Subcommand(
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
    meta=CommandMeta(description="每日签到，能够抽签和获得积分"),
)

__plugin_meta__ = PluginMetadata(
    name="签到",
    description=singin_command.meta.description,
    usage=singin_command.get_help(),
    config=None,
)

DATA_PATH = path.get_data_path("signin")

signin_matcher = on_alconna(
    singin_command,
    aliases={"签到"},
    block=True,
)


@signin_matcher.assign("themes")
async def _():
    await signin_matcher.finish("所有主题：\n\n" + "\n".join(fortune.get_themes()))


@signin_matcher.handle()
async def _(event: Event, theme: Query[str] = Query("theme", "random")):
    theme_name = theme.result.strip().lower()

    # 获取 uid
    platform_id = event.get_user_id()
    if not user.platform_id_user_exists(platform_id):
        await signin_matcher.finish("你还没有注册")
    user_id = user.get_uid(platform_id)

    today_record = signin.get_today_record(user_id)

    if today_record is None:
        title, content = fortune.get_random_copywrite()
        signin.set_today_record(user_id, title, content)
    else:
        title = today_record.title
        content = today_record.content

    image: bytes | None = None
    if await util.can_send_segment(Image):
        if (
            today_record is not None
            and theme_name == "random"
            and (DATA_PATH / f"{user_id}.png").exists()
        ):
            image = (DATA_PATH / f"{user_id}.png").read_bytes()
        else:
            image = await fortune.generate_image(title, content, theme_name)

    await signin_matcher.finish(
        await signin.generate_message(
            title,
            content,
            today_record is not None,
            image,
        )
    )
