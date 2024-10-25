from arclet.alconna import CommandMeta
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, Alconna, Image, Subcommand

from canrotbot.essentials.libraries import user, economy, util
from . import arknights, data

arknights_command = Alconna(
    "明日方舟",
    Subcommand("gacha", alias=["十连", "抽卡"], help_text="来一发十连！"),
    Subcommand(
        "gachainfo",
        alias=[
            "抽卡记录",
            "抽卡统计",
            "抽卡历史",
            "十连历史",
            "十连统计",
            "寻访历史",
            "寻访统计",
        ],
        help_text="查看抽卡记录",
    ),
    meta=CommandMeta(description="现在只做了抽卡，未来会加的（画饼"),
)

__plugin_meta__ = PluginMetadata(
    name="明日方舟助手",
    description=arknights_command.meta.description,
    usage=arknights_command.get_help(),
    config=None,
)


arknights_matcher = on_alconna(
    arknights_command,
    aliases={"arknights"},
    block=True,
)


@arknights_matcher.assign("gacha")
async def _():
    uid = user.get_uid()
    if not uid:
        await arknights_matcher.finish("你还没有账号喵~")

    # 付钱
    if not economy.pay(uid, 25, "方舟十连"):
        await arknights_matcher.finish("你的余额不足喵~")

    # 付款提示
    await arknights_matcher.send("你的二十五个胡萝卜片我就收下了喵~")

    # 寻访
    operators = arknights.generate_gacha(arknights.get_last_six_star(uid))
    arknights.save_gacha_history(uid, operators)

    # 发送消息
    await arknights_matcher.send(arknights.generate_gacha_text(operators))
    if await util.can_send_segment(Image):
        await arknights_matcher.send(
            Image(raw=await arknights.generate_gacha_image(operators))
        )
    await arknights_matcher.finish()


@arknights_matcher.assign("gachainfo")
async def _():
    uid = user.get_uid()
    if not uid:
        await arknights_matcher.finish("你还没有账号喵~")

    result = arknights.get_gacha_statistics(uid)

    if result["times"] == 0:
        # 未抽过卡
        await arknights_matcher.finish("你还没有抽过卡喵~")
    else:
        msg = (
            "明日方舟抽卡统计: \n"
            f"寻访次数: {result['times']}\n"
            f"消耗合成玉: {result['times'] * 600}\n"
            f"= 至纯源石: {round(result['times'] * 600 / 180, 2)}\n"
            f"= RMB: {round(result['times'] * 600 / 180 * 6, 2)}\n"
            f"3星干员: {result['three_stars']}\n"
            f"4星干员: {result['four_stars']}\n"
            f"5星干员: {result['five_stars']}\n"
            f"6星干员: {result['six_stars']}\n"
            f"距离上次抽到6星次数: {result['last_six_star']}"
        )
        await arknights_matcher.finish(msg)


@arknights_matcher.handle()
async def _():
    await arknights_matcher.finish(arknights_command.get_help())
