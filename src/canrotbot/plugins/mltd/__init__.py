from datetime import datetime

from arclet.alconna import Alconna, Option, Args
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Query,
    AlconnaQuery,
    UniMessage,
    Image,
    Text,
)

import canrotbot.libraries.mltd as libmltd
from canrotbot.essentials.libraries import user, economy, util
from . import mltd

__plugin_meta__ = PluginMetadata(
    name="MLTD",
    description="偶像大师-百万现场剧场时光有关的功能",
    usage="/<mltd> <功能还不知道有什么>",
    config=None,
)


def iso8601_to_local(iso8601: str) -> str:
    return (
        datetime.fromisoformat(iso8601).astimezone().strftime("%Y年%m月%d日 %H:%M:%S")
    )


_command = on_alconna(
    Alconna(
        "mltd",
        Option(
            "event",
            alias=["活动", "events"],
        ),
        Option(
            "card",
            Args["query", str],
            alias=["查卡"],
        ),
        Option(
            "gasha",
            alias=["抽卡", "十连", "gacha"],
        ),
        Option(
            "update",
            alias=["更新"],
        ),
    ),
    block=True,
)


@_command.assign("event")
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
        await _command.finish(msg)
    else:
        await _command.finish("现在还没有活动喵~")


@_command.assign("card")
async def _(query: Query[str] = AlconnaQuery("card", "query")):
    if await util.can_send_segment(Image):
        await _command.send("正在搜索喵~")
        card = libmltd.search_card(query.result.strip())
        await _command.finish(Image(raw=await mltd.generate_card_info_image(card)))
    await _command.finish("这里不支持发送图片所以没法查卡喵~")


@_command.assign("gasha")
async def _():
    uid = user.get_uid()
    if not economy.pay(uid, 25, "mltd 十连"):
        await _command.finish("你没有足够的胡萝卜片喵~")
    await _command.send("谢谢你的25个胡萝卜片喵~")
    img, data = await mltd.gasha()
    if await util.can_send_segment(Image):
        await _command.finish(Image(raw=img))
    else:
        txt_msg = ""
        for card in data:
            txt_msg += f"{card['rarity']}星 {card['name']}\n"
        await _command.finish(txt_msg.strip())


@_command.assign("update")
async def _():
    await _command.send("正在更新卡片数据喵~")
    await libmltd.load_cards(True)
    await _command.finish("更新完毕喵~")


@_command.handle()
async def _():
    await _command.finish(__plugin_meta__.usage)
