from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    Args,
    Arparma,
    Subcommand,
    Query,
)

from canrotbot.essentials.libraries import user, economy, util

__plugin_meta__ = PluginMetadata(
    name="经济系统",
    description="机器人经济系统，包括查询、转账等",
    usage="经济服务帮助:\n"
    "用法: /<economy|钱包|银行|经济> [操作]\n"
    "操作:\n"
    "info|信息: 查看账户信息\n"
    "transfer|转账 <platform_id|uid> <金额>: 向另一个用户转账",
    config=None,
)

_economy_command = on_alconna(
    Alconna(
        "economy",
        Subcommand("info", alias={"信息", "balance", "余额"}),
        Subcommand(
            "transfer", Args["transferee", str]["amount", float], alias={"转账"}
        ),
    ),
    aliases={"钱包", "银行", "经济", "bank"},
    block=True,
)


@_economy_command.handle()
async def _(event: Event, result: Arparma):
    if not result.subcommands:
        await _economy_command.finish(__plugin_meta__.usage)

    # 检查是否注册过
    platform_id = event.get_user_id()
    if not user.platform_id_user_exists(platform_id):
        await _economy_command.finish(f"platform_id: {platform_id}\n未注册")


@_economy_command.assign("info")
async def _(event: Event):
    platform_id = event.get_user_id()
    uid = user.get_uid()
    final = (
        f"platform_id: {platform_id}\n"
        f"uid: {uid}\n"
        f"当前余额: {economy.get_balance(uid)} 胡萝卜片\n\n"
        f"最近五条交易记录:"
    )

    for i in economy.get_transactions(uid, 5):
        final += (
            f"\n时间: {i.time.strftime('%Y-%m-%d %H:%M:%S')}"
            f"\n变动: {i.amount}"
            f"\n余额: {i.balance}"
            f"\n备注: {i.description}"
            f"\n{util.MESSAGE_SPLIT_LINE}"
        )
    await _economy_command.finish(final.strip())


@_economy_command.assign("transfer")
async def _(
    transferee: Query[str] = Query("transferee"),
    amount: Query[float] = Query("amount"),
):
    from_uid = user.get_uid()
    to_uid = 0

    if transferee.result.isdigit():
        to_uid = int(transferee.result)

    if not user.uid_user_exists(to_uid):
        to_uid = 0
        to_platform_id = transferee.result
        if user.platform_id_user_exists(to_platform_id):
            to_uid = user.get_uid(to_platform_id)

    if to_uid == 0:
        await _economy_command.finish("未找到此用户")

    if economy.transfer(from_uid, to_uid, amount.result):
        await _economy_command.finish(
            f"向 {transferee.result} 转账 {amount.result} 个胡萝卜片成功"
        )
    else:
        await _economy_command.finish(
            f"余额不足，向 {transferee.result} 转账 {amount.result} 个胡萝卜片失败"
        )
