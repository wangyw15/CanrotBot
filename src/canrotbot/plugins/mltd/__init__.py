from datetime import datetime

from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Image,
    Query,
    Subcommand,
    Text,
    UniMessage,
    on_alconna,
)

import canrotbot.libraries.mltd as libmltd
from canrotbot.essentials.libraries import economy, user, util

from . import mltd

mltd_command = Alconna(
    "mltd",
    Subcommand(
        "events",
        alias=["活动", "event"],
    ),
    Subcommand(
        "card",
        Args["query", str],
        alias=["查卡"],
    ),
    Subcommand(
        "gasha",
        alias=["抽卡", "十连", "gacha"],
    ),
    Subcommand(
        "update",
        alias=["更新"],
    ),
    meta=CommandMeta(description="偶像大师-百万现场剧场时光有关的功能"),
)

__plugin_meta__ = PluginMetadata(
    name="MLTD",
    description=mltd_command.meta.description,
    usage=mltd_command.get_help(),
    config=None,
)


mltd_matcher = on_alconna(
    mltd_command,
    aliases={"麻辣土豆"},
    block=True,
)


def iso8601_to_local(iso8601: str) -> str:
    return (
        datetime.fromisoformat(iso8601).astimezone().strftime("%Y年%m月%d日 %H:%M:%S")
    )


@mltd_matcher.assign("events")
async def _():
    data = await libmltd.get_events()
    if data:
        msg = UniMessage()
        msg.append(Text("现在正在进行的活动:"))
        for mltd_event in data:
            # 活动信息
            text_msg = ""
            text_msg += (
                f"{mltd_event['name']}\n"
                f"类型: {libmltd.EVENT_TYPE[mltd_event['type'] - 1]}\n"
                f"Appeal 类型: {libmltd.APPEAL_TYPE[mltd_event['appealType']]}\n"
                f"活动开始时间: {iso8601_to_local(mltd_event['schedule']['beginAt'])}\n"
                f"活动结束时间: {iso8601_to_local(mltd_event['schedule']['endAt'])}\n"
                f"页面开放时间: {iso8601_to_local(mltd_event['schedule']['pageOpenedAt'])}\n"
                f"页面关闭时间: {iso8601_to_local(mltd_event['schedule']['pageClosedAt'])}\n"
            )
            text_msg += (
                f"加速开始时间: {iso8601_to_local(mltd_event['schedule']['boostBeginAt'])}\n"
                if mltd_event["schedule"]["boostBeginAt"]
                else ""
            )
            text_msg += (
                f"加速结束时间: {iso8601_to_local(mltd_event['schedule']['boostEndAt'])}\n"
                if mltd_event["schedule"]["boostEndAt"]
                else ""
            )
            text_msg += (
                f"活动物品: {mltd_event['item']['name']}"
                if mltd_event["item"]["name"]
                else ""
            )
            # 构建信息
            msg.append(Text("\n\n"))
            if await util.can_send_segment(Image):
                # 活动封面
                img_url = f"https://storage.matsurihi.me/mltd/event_bg/{str(mltd_event['id']).zfill(4)}.png"
                msg.append(Image(url=img_url))
            msg.append(Text(text_msg))
        await mltd_matcher.finish(msg)
    else:
        await mltd_matcher.finish("现在还没有活动喵~")


@mltd_matcher.assign("card")
async def _(query: Query[str] = Query("query")):
    if await util.can_send_segment(Image):
        await mltd_matcher.send("正在搜索喵~")
        card = libmltd.search_card(query.result.strip())
        await mltd_matcher.finish(Image(raw=await mltd.generate_card_info_image(card)))
    await mltd_matcher.finish("这里不支持发送图片所以没法查卡喵~")


@mltd_matcher.assign("gasha")
async def _():
    uid = user.get_uid()
    if not economy.pay(uid, 25, "mltd 十连"):
        await mltd_matcher.finish("你没有足够的胡萝卜片喵~")
    await mltd_matcher.send("谢谢你的25个胡萝卜片喵~")
    img, data = await mltd.gasha()
    if await util.can_send_segment(Image):
        await mltd_matcher.finish(Image(raw=img))
    else:
        txt_msg = ""
        for card in data:
            txt_msg += f"{card['rarity']}星 {card['name']}\n"
        await mltd_matcher.finish(txt_msg.strip())


@mltd_matcher.assign("update")
async def _():
    await mltd_matcher.send("正在更新卡片数据喵~")
    await libmltd.load_cards(True)
    await mltd_matcher.finish("更新完毕喵~")


@mltd_matcher.handle()
async def _():
    await mltd_matcher.finish(__plugin_meta__.usage)
