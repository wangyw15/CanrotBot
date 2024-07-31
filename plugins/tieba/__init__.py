from arclet.alconna import Alconna, Option, Args
from nonebot import get_bot
from nonebot.adapters import Bot, Event
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Query, AlconnaQuery
from sqlalchemy import select, insert, delete
from nonebot_plugin_apscheduler import scheduler

from essentials.libraries import user
from storage import database
from . import data, signin

__plugin_meta__ = PluginMetadata(
    name="贴吧",
    description="比如贴吧签到、签到和签到",
    usage="/tieba signin",
    config=None,
)


_command = on_alconna(
    Alconna(
        "tieba",
        Option(
            "bind",
            Args["bduss", str]["stoken", str]["alias", str, ""],
            alias=["绑定"],
            help_text="绑定贴吧账号",
        ),
        Option(
            "unbind",
            Args["account_id", int, 0],
            alias=["解绑"],
            help_text="解绑贴吧账号",
        ),
        Option("list", alias=["绑定列表"], help_text="查看绑定列表"),
        Option(
            "subscribe",
            Args["account_id", int, 0],
            alias=["订阅"],
            help_text="订阅签到结果",
        ),
        Option(
            "unsubscribe",
            Args["account_id", int, 0],
            alias=["退订"],
            help_text="退订签到结果",
        ),
        Option(
            "sign", Args["account_id", int, 0], alias=["签到"], help_text="手动一键签到"
        ),
        Option(
            "signinfo",
            Args["account_id", int, 0],
            alias=["签到信息"],
            help_text="查看签到信息",
        ),
    ),
    aliases={"贴吧"},
    block=True,
)


@_command.assign("bind")
async def _(
    bduss_query: Query[str] = AlconnaQuery("bduss"),
    stoken_query: Query[str] = AlconnaQuery("stoken"),
    alias_query: Query[str] = AlconnaQuery("alias", ""),
):
    uid = await user.get_uid()
    if not uid:
        await _command.finish("还未注册或绑定账号")

    bduss = bduss_query.result.strip()
    stoken = stoken_query.result.strip()
    alias = alias_query.result.strip()

    with database.get_session().begin() as session:
        if alias:
            if session.execute(
                select(data.BaiduAccount).where(
                    data.BaiduAccount.owner_user_id == uid,  # type: ignore
                    data.BaiduAccount.alias == alias,  # type: ignore
                )
            ).scalar_one_or_none():
                await _command.finish("该别名已被使用")
        session.execute(
            insert(data.BaiduAccount).values(
                owner_user_id=uid,
                bduss=bduss,
                stoken=stoken,
                alias=alias,
            )
        )
    await _command.finish("绑定成功")


@_command.assign("unbind")
async def _(account_id_query: Query[int] = AlconnaQuery("account_id", 0)):
    uid = await user.get_uid()
    if not uid:
        await _command.finish("还未注册或绑定账号")

    account_id = account_id_query.result

    with database.get_session().begin() as session:
        if account_id:
            # 删除订阅
            session.execute(
                delete(data.TiebaSignResultSubscriber).where(
                    data.TiebaSignResultSubscriber.account_id == account_id,  # type: ignore
                )
            )
            # 删除账号
            session.execute(
                delete(data.BaiduAccount).where(
                    data.BaiduAccount.owner_user_id == uid,  # type: ignore
                    data.BaiduAccount.id == account_id,  # type: ignore
                )
            )
        else:
            # 删除订阅
            accounts = (
                session.execute(
                    select(data.BaiduAccount).where(
                        data.BaiduAccount.owner_user_id == uid  # type: ignore
                    )
                )
                .scalars()
                .all()
            )
            for account in accounts:
                session.execute(
                    delete(data.TiebaSignResultSubscriber).where(
                        data.TiebaSignResultSubscriber.account_id == account.id,
                    )
                )
            # 删除账号
            session.execute(
                delete(data.BaiduAccount).where(data.BaiduAccount.owner_user_id == uid)  # type: ignore
            )

    if account_id:
        await _command.finish(f"账号 {account_id} 解绑成功")
    else:
        await _command.finish("所有账号解绑成功")


@_command.assign("list")
async def _():
    uid = await user.get_uid()
    if not uid:
        await _command.finish("还未注册或绑定账号")

    msg = "已绑定账号"

    with database.get_session().begin() as session:
        accounts = (
            session.execute(
                select(data.BaiduAccount).where(data.BaiduAccount.owner_user_id == uid)  # type: ignore
            )
            .scalars()
            .all()
        )

        if not accounts:
            await _command.finish("还未绑定贴吧账号")
        for account in accounts:
            if account.alias:
                msg += f"\n{account.id}({account.alias}): {account.bduss[:5]}...{account.bduss[-5:]}"
            else:
                msg += f"\n{account.id}: {account.bduss[:5]}...{account.bduss[-5:]}"

    await _command.finish(msg)


@_command.assign("subscribe")
async def _(
    bot: Bot, event: Event, account_id_query: Query[int] = AlconnaQuery("account_id", 0)
):
    puid = event.get_user_id()
    uid = await user.get_uid()
    if not uid:
        await _command.finish("还未注册或绑定账号")

    account_id = account_id_query.result

    with database.get_session().begin() as session:
        if account_id:
            accounts = (
                session.execute(
                    select(data.BaiduAccount).where(
                        data.BaiduAccount.owner_user_id == uid,  # type: ignore
                        data.BaiduAccount.id == account_id,  # type: ignore
                    )
                )
                .scalars()
                .all()
            )
        else:
            accounts = (
                session.execute(
                    select(data.BaiduAccount).where(
                        data.BaiduAccount.owner_user_id == uid,  # type: ignore
                    )
                )
                .scalars()
                .all()
            )
        if not accounts:
            await _command.finish("还未绑定贴吧账号")

        for account in accounts:
            if session.execute(
                select(data.TiebaSignResultSubscriber).where(
                    data.TiebaSignResultSubscriber.account_id == account.id,  # type: ignore
                    data.TiebaSignResultSubscriber.puid == puid,  # type: ignore
                )
            ).scalar_one_or_none():
                continue
            session.execute(
                insert(data.TiebaSignResultSubscriber).values(
                    account_id=account.id,
                    puid=puid,
                    bot=bot.self_id,
                )
            )
    await _command.finish("订阅成功")


@_command.assign("unsubscribe")
async def _(event: Event, account_id_query: Query[int] = AlconnaQuery("account_id", 0)):
    puid = event.get_user_id()
    uid = await user.get_uid()
    if not uid:
        await _command.finish("还未注册或绑定账号")

    account_id = account_id_query.result

    with database.get_session().begin() as session:
        if account_id:
            session.execute(
                delete(data.TiebaSignResultSubscriber).where(
                    data.TiebaSignResultSubscriber.account_id == account_id,  # type: ignore
                    data.TiebaSignResultSubscriber.puid == puid,  # type: ignore
                )
            )
        else:
            session.execute(
                delete(data.TiebaSignResultSubscriber).where(
                    data.TiebaSignResultSubscriber.puid == puid,  # type: ignore
                )
            )

    if account_id:
        await _command.finish(f"账号 {account_id} 退订成功")
    else:
        await _command.finish("所有账号退订成功")


@_command.assign("sign")
async def _(account_id_query: Query[int] = AlconnaQuery("account_id", 0)):
    uid = await user.get_uid()
    if not uid:
        await _command.finish("还未注册或绑定账号")

    account_id = account_id_query.result
    signin_result: dict[int, list[signin.ForumSigninResult] | None] = {}

    with database.get_session().begin() as session:
        if account_id:
            accounts = (
                session.execute(
                    select(data.BaiduAccount).where(
                        data.BaiduAccount.owner_user_id == uid,  # type: ignore
                        data.BaiduAccount.id == account_id,  # type: ignore
                    )
                )
                .scalars()
                .all()
            )
        else:
            accounts = (
                session.execute(
                    select(data.BaiduAccount).where(
                        data.BaiduAccount.owner_user_id == uid,  # type: ignore
                    )
                )
                .scalars()
                .all()
            )
        if not accounts:
            await _command.finish("还未绑定贴吧账号")
        for account in accounts:
            signin_result[account.id] = await signin.signin(
                account.bduss, account.stoken
            )

    msg = "签到结果"

    for account_id, result in signin_result.items():
        if result:
            msg += f"\n账号 {account_id}\n{signin.generate_text_result(result)}"
        else:
            msg += f"\n账号 {account_id} 签到失败"
    await _command.finish(msg)


@_command.assign("signinfo")
async def _(account_id_query: Query[int] = AlconnaQuery("account_id", 0)):
    # TODO 记得做
    await _command.finish("暂未实现")


@scheduler.scheduled_job("cron", hour="0", id="tieba_signin")
async def _():
    with database.get_session().begin() as session:
        accounts = session.execute(select(data.BaiduAccount)).scalars().all()
        for account in accounts:
            result = await signin.signin(account.bduss, account.stoken)

            subscribers = (
                session.execute(
                    select(data.TiebaSignResultSubscriber).where(
                        data.TiebaSignResultSubscriber.account_id == account.id,  # type: ignore
                    )
                )
                .scalars()
                .all()
            )
            for subscriber in subscribers:
                # TODO 支持多平台
                if subscriber.puid.startswith("qq_"):
                    bot = get_bot(subscriber.bot)
                    await bot.call_api(
                        "send_private_msg",
                        user_id=subscriber.puid[3:],
                        message=signin.generate_text_result(result),
                    )
