from arclet.alconna import Alconna, Option
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, UniMessage, Image, Text

from essentials.libraries import user, economy, util
from . import arknights, data

__plugin_meta__ = PluginMetadata(
    name="明日方舟助手",
    description="现在只做了抽卡，未来会加的（画饼",
    usage=(
        "/<arknights|粥|舟|方舟|明日方舟> <命令>\n"
        + "命令列表:\n"
        + "十连: 一发十连！\n"
        + "抽卡记录: 查看抽卡记录"
    ),
    config=None,
)


_command = on_alconna(
    Alconna(
        "明日方舟",
        Option("十连", alias=["gacha", "抽卡"], help_text="来一发十连！"),
        Option(
            "抽卡记录",
            alias=[
                "gachainfo",
                "抽卡统计",
                "抽卡历史",
                "十连历史",
                "十连统计",
                "寻访历史",
                "寻访统计",
            ],
            help_text="查看抽卡记录",
        ),
    ),
    aliases={"arknights"},
    block=True,
)


@_command.assign("十连")
async def _():
    uid = user.get_uid()
    if not uid:
        await _command.finish("你还没有账号喵~")

    # 付钱
    if not economy.pay(uid, 25, "方舟十连"):
        await _command.finish("你的余额不足喵~")

    # 付款提示
    await _command.send("你的二十五个胡萝卜片我就收下了喵~")

    # 寻访
    operators = arknights.generate_gacha(arknights.get_last_six_star(uid))
    arknights.save_gacha_history(uid, operators)

    # 生成消息
    msg = UniMessage()
    msg.append(Text(arknights.generate_gacha_text(operators)))
    if await util.can_send_segment(Image):
        msg.append(Image(raw=await arknights.generate_gacha_image(operators)))

    await _command.finish(msg)


@_command.assign("抽卡记录")
async def _():
    uid = user.get_uid()
    if not uid:
        await _command.finish("你还没有账号喵~")

    result = arknights.get_gacha_statistics(uid)

    if result["times"] == 0:
        # 未抽过卡
        await _command.finish("你还没有抽过卡喵~")
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
        await _command.finish(msg)


@_command.handle()
async def _():
    await _command.finish(__plugin_meta__.usage)
