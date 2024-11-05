from nonebot import logger
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    MsgTarget,
    Query,
    Subcommand,
    Text,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_apscheduler import scheduler

from canrotbot.essentials.libraries import user

from . import data, tieba

tieba_command = Alconna(
    "tieba",
    Subcommand(
        "add",
        Args["bduss", str]["stoken", str]["alias", str, ""],
        alias=["绑定"],
        help_text="绑定贴吧账号",
    ),
    Subcommand(
        "delete",
        Args["delete_account_id", int],
        alias=["解绑"],
        help_text="解绑贴吧账号",
    ),
    Subcommand("list", alias=["绑定列表"], help_text="查看绑定列表"),
    Subcommand(
        "subscribe",
        Args["subscribe_account_id", int],
        alias=["订阅"],
        help_text="订阅签到结果",
    ),
    Subcommand(
        "unsubscribe",
        Args["unsubscribe_account_id", int],
        alias=["退订"],
        help_text="退订签到结果",
    ),
    Subcommand(
        "sign",
        Args["sign_account_id", int, 0],
        alias=["签到"],
        help_text="手动一键签到",
    ),
    Subcommand(
        "signinfo",
        Args["signinfo_account_id", int],
        alias=["签到信息"],
        help_text="查看最近一次签到信息",
    ),
    meta=CommandMeta(description="贴吧相关功能，如签到"),
)

__plugin_meta__ = PluginMetadata(
    name="贴吧",
    description=tieba_command.meta.description,
    usage=tieba_command.get_help(),
    config=None,
)

tieba_matcher = on_alconna(
    tieba_command,
    aliases={"贴吧"},
    block=True,
)


@tieba_matcher.assign("list")
async def _():
    uid = user.get_uid()
    if not uid:
        await tieba_matcher.finish("还未注册或绑定账号")

    msg = "已绑定账号"

    accounts = tieba.get_all_owned_accounts(uid)
    if not accounts:
        await tieba_matcher.finish("还未绑定贴吧账号")
    for account in accounts:
        if account.alias:
            msg += f"\n{account.id}({account.alias}): {account.bduss[:5]}...{account.bduss[-5:]}"
        else:
            msg += f"\n{account.id}: {account.bduss[:5]}...{account.bduss[-5:]}"

    await tieba_matcher.finish(msg)


@tieba_matcher.assign("add")
async def _(
    bduss_query: Query[str] = Query("bduss"),
    stoken_query: Query[str] = Query("stoken"),
    alias_query: Query[str] = Query("alias", ""),
):
    uid = user.get_uid()
    if not uid:
        await tieba_matcher.finish("还未注册或绑定账号")

    bduss = bduss_query.result.strip()
    stoken = stoken_query.result.strip()
    alias = alias_query.result.strip()

    if tieba.check_alias_exists(uid, alias):
        await tieba_matcher.finish("该别名已被使用")

    tieba.add_account(uid, bduss, stoken, alias)
    await tieba_matcher.finish("绑定成功")


@tieba_matcher.assign("delete")
async def _(account_id_query: Query[int] = Query("delete_account_id")):
    uid = user.get_uid()
    if not uid:
        await tieba_matcher.finish("还未注册或绑定账号")

    accounts = tieba.get_all_owned_accounts(uid)
    if not accounts:
        await tieba_matcher.finish("还未绑定贴吧账号")

    account_id = account_id_query.result
    if not tieba.check_account_exists(uid, account_id):
        await tieba_matcher.finish("你没有这个 ID 对应的百度账号")

    tieba.unsubscribe_all(account_id)
    tieba.delete_account(uid, account_id)

    await tieba_matcher.finish(f"账号 {account_id} 解绑成功")


@tieba_matcher.assign("subscribe")
async def _(
    target: MsgTarget, account_id_query: Query[int] = Query("subscribe_account_id")
):
    uid = user.get_uid()
    if not uid:
        await tieba_matcher.finish("还未注册或绑定账号")

    accounts = tieba.get_all_owned_accounts(uid)
    if not accounts:
        await tieba_matcher.finish("还未绑定贴吧账号")

    account_id = account_id_query.result
    if not tieba.check_account_exists(uid, account_id):
        await tieba_matcher.finish("你没有这个 ID 对应的百度账号")

    tieba.subscribe(account_id, target)
    await tieba_matcher.finish("订阅成功")


@tieba_matcher.assign("unsubscribe")
async def _(
    target: MsgTarget, account_id_query: Query[int] = Query("unsubscribe_account_id")
):
    uid = user.get_uid()
    if not uid:
        await tieba_matcher.finish("还未注册或绑定账号")

    accounts = tieba.get_all_owned_accounts(uid)
    if not accounts:
        await tieba_matcher.finish("还未绑定贴吧账号")

    account_id = account_id_query.result
    if not tieba.check_account_exists(uid, account_id):
        await tieba_matcher.finish("你没有这个 ID 对应的百度账号")

    tieba.unsubscribe(account_id, target)
    await tieba_matcher.finish(f"账号 {account_id} 退订成功")


@tieba_matcher.assign("sign")
async def _(account_id_query: Query[int] = Query("sign_account_id", 0)):
    uid = user.get_uid()
    if not uid:
        await tieba_matcher.finish("还未注册或绑定账号")

    accounts = tieba.get_all_owned_accounts(uid)
    if not accounts:
        await tieba_matcher.finish("还未绑定贴吧账号")

    account_id = account_id_query.result
    signin_result: dict[int, list[data.ForumSigninResultData]] = {}
    accounts: list[data.Account] = []

    if account_id:
        if not tieba.check_account_exists(uid, account_id):
            await tieba_matcher.finish("你没有这个 ID 对应的百度账号")
        accounts.append(tieba.get_account(uid, account_id))
    else:
        accounts = tieba.get_all_owned_accounts(uid)

    for account in accounts:
        result = await tieba.signin(account)
        signin_result[account_id] = result
        tieba.save_signin_result(account_id, result)

    msg = "签到结果"

    for account_id, result in signin_result.items():
        if result:
            msg += f"\n账号 {account_id}\n{tieba.generate_text_result(result)}"
        else:
            msg += f"\n账号 {account_id} 签到失败"
    await tieba_matcher.finish(msg)


@tieba_matcher.assign("signinfo")
async def _(account_id_query: Query[int] = Query("signinfo_account_id")):
    uid = user.get_uid()
    if not uid:
        await tieba_matcher.finish("还未注册或绑定账号")

    accounts = tieba.get_all_owned_accounts(uid)
    if not accounts:
        await tieba_matcher.finish("还未绑定贴吧账号")

    account_id = account_id_query.result
    if not tieba.check_account_exists(uid, account_id):
        await tieba_matcher.finish("你没有这个 ID 对应的百度账号")

    result = tieba.get_latest_signin_result(account_id)
    if not result:
        await tieba_matcher.finish("还未签到过")
    await tieba_matcher.finish("签到结果\n" + tieba.generate_text_result(result))


@scheduler.scheduled_job("cron", hour="0", id="tieba_signin")
async def run_daily_signin():
    logger.info("Start tieba signin")
    accounts = tieba.get_all_accounts()
    for account in accounts:
        result = await tieba.signin(account)
        tieba.save_signin_result(account.id, result)

        display_name = tieba.get_account_alias(account.id)
        if not display_name:
            display_name = str(account.id)

        subscribers = tieba.get_signin_result_subscribers(account.id)
        for subscriber in subscribers:
            await UniMessage(
                Text(f"\n贴吧账号 {display_name}\n{tieba.generate_text_result(result)}")
            ).send(subscriber)
