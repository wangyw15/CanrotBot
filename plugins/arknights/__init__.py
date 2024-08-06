from arclet.alconna import Alconna, Option
from nonebot.exception import FinishedException
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import on_alconna, UniMessage, Image, Text, SerializeFailed
from sqlalchemy import select

from essentials.libraries import user, economy, database
from . import arknights, data

__plugin_meta__ = PluginMetadata(
    name="明日方舟助手",
    description="现在只做了抽卡，未来会加的（画饼",
    usage="/<arknights|粥|舟|方舟|明日方舟> <命令>",
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
    # 抽卡
    img, operators = await arknights.generate_gacha(uid)
    # 付款提示
    await _command.send("你的二十五个胡萝卜片我就收下了喵~")
    # 生成消息
    msg = UniMessage()
    # 列出抽到的干员
    msg.append(Text("明日方舟抽卡结果: \n"))
    for operator in operators:
        msg += Text(f"{operator['rarity'] + 1}星 {operator['name']}\n")
    msg.append(Image(raw=img))
    try:
        await _command.finish(msg)
    except SerializeFailed:
        msg.pop()
        await _command.finish(msg)
    except FinishedException as e:
        raise e
    except Exception as e:
        await _command.finish(str(e))


@_command.assign("抽卡记录")
async def _():
    uid = user.get_uid()
    if not uid:
        await _command.finish("你还没有账号喵~")

    with database.get_session().begin() as session:
        gacha_result = session.execute(
            select(data.Statistics).where(data.Statistics.user_id.is_(uid))
        ).scalar_one_or_none()
        if gacha_result.times == 0:
            # 未抽过卡
            await _command.finish("你还没有抽过卡喵~")
        else:
            msg = (
                "明日方舟抽卡统计: \n"
                f"寻访次数: {gacha_result.times}\n"
                f"消耗合成玉: {gacha_result.times * 600}\n"
                f"= 至纯源石: {round(gacha_result.times * 600 / 180, 2)}\n"
                f"= RMB: {round(gacha_result.times * 600 / 180 * 6, 2)}\n"
                f"3星干员: {gacha_result.three_stars}\n"
                f"4星干员: {gacha_result.four_stars}\n"
                f"5星干员: {gacha_result.five_stars}\n"
                f"6星干员: {gacha_result.six_stars}\n"
                f"距离上次抽到6星次数: {gacha_result.last_six_star}"
            )
            await _command.finish(msg)


@_command.handle()
async def _():
    await _command.finish(
        "用法: "
        + __plugin_meta__.usage
        + "\n命令列表:\n十连: 一发十连！\n抽卡记录: 查看抽卡记录"
    )
