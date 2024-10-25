from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    Args,
    Subcommand,
    Query,
)

from canrotbot.essentials.libraries import user

__plugin_meta__ = PluginMetadata(
    name="用户服务",
    description="用户服务，包括绑定、注册等",
    usage=(
        "用户服务帮助:\n"
        "用法: /<user|用户|我> [操作]\n"
        "操作:\n"
        "register|reg|注册: 注册一个新用户\n"
        "info|信息: 查看用户信息\n"
        "bind|绑定 <platform_id>: 绑定一个platform_id\n"
        "unbind|解绑|解除绑定|取消绑定 <platform_id>: 解除绑定platform_id"
    ),
    config=None,
)

_user_command = on_alconna(
    Alconna(
        "user",
        Subcommand("info", alias={"信息"}),
        Subcommand("register", alias={"reg", "注册"}),
        Subcommand("bind", Args["platform_id", str], alias={"绑定"}),
        Subcommand(
            "unbind", Args["platform_id", str], alias={"解绑", "解除绑定", "取消绑定"}
        ),
    ),
    aliases={"用户", "我"},
    block=True,
)


@_user_command.assign("info")
async def _(event: Event):
    platform_id = event.get_user_id()
    if not user.platform_id_user_exists(platform_id):
        await _user_command.finish(f"platform_id: {platform_id}\n未注册")
    else:
        uid = user.get_uid()
        msg = f"当前 platform_id: {platform_id}\nuid: {uid}\n已绑定的 platform_id:\n"
        msg += "\n".join(user.get_bind_by_uid(uid))
        await _user_command.finish(msg)


@_user_command.assign("register")
async def _(event: Event):
    platform_id = event.get_user_id()
    if user.platform_id_user_exists(platform_id):
        await _user_command.finish("你已经注册过了")
    else:
        uid = user.register(platform_id)
        await _user_command.finish(f"注册成功，你的 UID 是 {uid}")


@_user_command.assign("bind")
async def _(platform_id: Query[str] = Query("platform_id")):
    if user.platform_id_user_exists(platform_id.result):
        await _user_command.finish("此 platform_id 已经绑定或注册过了")
    uid = user.get_uid()
    user.bind(platform_id.result, uid)
    await _user_command.finish("绑定成功")


@_user_command.assign("unbind")
async def _(platform_id: Query[str] = Query("platform_id")):
    if not user.platform_id_user_exists(platform_id.result):
        await _user_command.finish("此 platform_id 还未绑定或注册")
    user.unbind(platform_id.result)
    await _user_command.finish("解绑成功")


@_user_command.handle()
async def _():
    await _user_command.finish(__plugin_meta__.usage)
