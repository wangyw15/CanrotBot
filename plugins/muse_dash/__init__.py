from arclet.alconna import Alconna, Option, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Query, AlconnaQuery, Image
from sqlalchemy import select, insert, update, delete

from essentials.libraries import user, util
from storage import database
from . import muse_dash, data

__plugin_meta__ = PluginMetadata(
    name="MuseDash查分",
    description="从 https://musedash.moe/ 查询玩家数据",
    usage="/<musedash> [功能]\n"
    "功能: \n"
    "<help|帮助>: 显示此帮助信息\n"
    "<bind|绑定> <玩家名|id>: 绑定 MuseDash.moe 账号\n"
    "<unbind|解绑>: 解绑 MuseDash.moe 账号\n"
    "<玩家名>: 查询玩家数据\n"
    "<me|我|我的|info|信息>\n"
    "/<musedash>: 查询已绑定账号的数据",
    config=None,
)

_command = on_alconna(
    Alconna(
        "musedash",
        Option(
            "bind",
            Args["target", str],
            alias=["绑定"],
        ),
        Option(
            "unbind",
            alias=["解绑"],
        ),
        Option(
            "info",
            alias=["我", "我的", "me", "信息"],
        ),
        Args["target", str, ""],
    ),
    block=True,
)


@_command.assign("bind")
async def _(target: Query[str] = AlconnaQuery("target")):
    uid = user.get_uid()
    query = select(data.MuseDashAccount).where(data.MuseDashAccount.user_id.is_(uid))
    # 绑定账号
    if not uid:
        await _command.finish("你还未注册账号")

    player_name = target.result.strip()
    # 获取玩家名和 ID
    if len(player_name) == 32:
        player_id = player_name
        player_name = (await muse_dash.fetch_muse_dash_player_data(player_id))["name"]
    else:
        player_id = await muse_dash.search_muse_dash_player_id(player_name)
    if player_id and player_name:
        with database.get_session().begin() as session:
            if session.execute(query).first() is not None:
                session.execute(
                    update(data.MuseDashAccount)
                    .where(data.MuseDashAccount.user_id.is_(uid))
                    .values(player_name=player_name, player_id=player_id)
                )
            else:
                session.execute(
                    insert(data.MuseDashAccount).values(
                        user_id=uid, player_name=player_name, player_id=player_id
                    )
                )
            session.commit()
        await _command.send(
            f"绑定成功\n玩家名: {player_name}\nMuseDash.moe ID: {player_id}"
        )
    else:
        await _command.finish("绑定失败")


@_command.assign("unbind")
async def _():
    uid = user.get_uid()
    # 解绑账号
    if not uid:
        await _command.finish("你还未注册账号")
    with database.get_session().begin() as session:
        session.execute(
            delete(data.MuseDashAccount).where(data.MuseDashAccount.user_id.is_(uid))
        )
        session.commit()
    await _command.finish("解绑成功")


@_command.assign("info")
async def _():
    uid = user.get_uid()
    query = select(data.MuseDashAccount).where(data.MuseDashAccount.user_id.is_(uid))

    # 检查绑定信息
    if not uid:
        await _command.finish("你还未注册账号")
    with database.get_session().begin() as session:
        account = session.execute(query).scalar_one_or_none()
    if account is not None:
        await _command.finish(
            f"已绑定账号信息:\n玩家名: {account.player_name}\nMuseDash.moe ID: {account.player_id}"
        )
    else:
        await _command.finish(
            "您还没有绑定 MuseDash.moe 账号，请使用 /muse-dash help 查看帮助信息"
        )


@_command.handle()
async def _(target: Query[str] = AlconnaQuery("target", "")):
    target = target.result.strip()
    player_id = ""

    if target:
        # 获取玩家信息
        player_name = target
        # 获取玩家 ID
        if len(player_name) == 32:
            player_id = player_name
        else:
            player_id = await muse_dash.search_muse_dash_player_id(player_name)
    else:
        uid = user.get_uid()
        query = select(data.MuseDashAccount).where(
            data.MuseDashAccount.user_id.is_(uid)
        )

        # 检查绑定信息
        if not uid:
            await _command.finish("你还未注册账号")
        with database.get_session().begin() as session:
            account = session.execute(query).scalar_one_or_none()
        if account is not None:
            player_id = account.player_id

    if player_id:
        await _command.send("正在查分喵~")
        if await util.can_send_segment(Image):
            await _command.finish(
                Image(raw=await muse_dash.generate_muse_dash_player_image(player_id))
            )
        else:
            msg = await muse_dash.generate_muse_dash_message(player_id)
            if msg:
                await _command.finish(msg)
            else:
                await _command.finish("查询失败")
