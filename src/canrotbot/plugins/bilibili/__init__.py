import typing
from datetime import datetime

from nonebot import on_fullmatch, on_regex
from nonebot.adapters.qq import Bot as QQBot
from nonebot.params import RegexGroup, RegexStr
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from nonebot_plugin_alconna import Image, Text, UniMessage

from canrotbot.essentials.libraries import util

from . import bilibili

__plugin_meta__ = PluginMetadata(
    name="Bilibili",
    description="哔哩哔哩相关，比如从B站url提取信息，还有展览信息",
    usage="B站url会自动触发",
    config=None,
)


def _generate_bilibili_message(data: dict, with_url: bool = True) -> str:
    # 描述删掉所有空行，并且只取前200个字符
    desc = "\n".join([x.strip() for x in data["desc"].split("\n") if x.strip() != ""])
    if len(desc) > 200:
        desc = desc[:200] + "..."
    # 视频发布时间
    date = datetime.fromtimestamp(data["pubdate"])
    # 生成信息
    msg = (
        f'标题: \n{data["title"]}\n'
        f'UP主: \n{data["owner"]["name"]}\n'
        f'发布时间: {date.strftime("%Y年%m月%d日 %H:%M:%S")}\n'
        f'播放: {data["stat"]["view"]}\n'
        f'弹幕: {data["stat"]["danmaku"]}\n'
        f'点赞: {data["stat"]["like"]}\n'
        f'投币: {data["stat"]["coin"]}\n'
        f"简介:\n{desc}"
    )
    if with_url:
        msg += f'\n视频链接: \nhttps://www.bilibili.com/video/{data["bvid"]}'

    return msg


bilibili_link_matcher = on_regex(bilibili.bilibili_vid_pattern, block=True)
bilibili_short_link_matcher = on_regex(
    r"https:\/\/b23.tv\/(?!BV)[0-9A-Za-z]{7}", block=True
)
bilibili_projects_matcher = on_fullmatch("我要看展", block=True)


@bilibili_link_matcher.handle()
@bilibili_short_link_matcher.handle()
@bilibili_projects_matcher.handle()
async def _(bot: QQBot, state: T_State):
    # 标注官方QQ机器人
    _ = bot.self_id  # 没啥用的一句
    state["official_qq"] = True


@bilibili_link_matcher.handle()
async def _(
    reg: typing.Annotated[tuple[typing.Any, ...], RegexGroup()], state: T_State
):
    data = await bilibili.fetch_video_data(reg[0])
    if data:
        final_msg = UniMessage()
        if await util.can_send_segment(Image):
            final_msg.append(Image(url=data["pic"]))
        final_msg.append(
            Text(
                _generate_bilibili_message(
                    data, with_url=not state.get("official_qq", False)
                )
            )
        )
        await bilibili_link_matcher.finish(await final_msg.export())
    await bilibili_link_matcher.finish()


@bilibili_short_link_matcher.handle()
async def _(reg: typing.Annotated[str, RegexStr()], state: T_State):
    vid = await bilibili.get_bvid_from_short_link(reg)
    if vid:
        data = await bilibili.fetch_video_data(vid)
        if data:
            final_msg = UniMessage()
            if await util.can_send_segment(Image):
                final_msg.append(Image(url=data["pic"]))
            final_msg.append(
                Text(
                    _generate_bilibili_message(
                        data, with_url=not state.get("official_qq", False)
                    )
                )
            )
            await bilibili_short_link_matcher.finish(await final_msg.export())
    await bilibili_short_link_matcher.finish()


@bilibili_projects_matcher.handle()
async def _(state: T_State):
    projects = await bilibili.fetch_all_projects()
    if projects:
        msg = "现在的正在进行的展览有:\n\n"
        for project in projects:
            start_time = datetime.strptime(project["start_time"], "%Y-%m-%d")
            try:
                end_time = datetime.strptime(project["end_time"], "%Y-%m-%d")
            except ValueError:
                end_time = datetime.strptime(
                    str(start_time.year) + "." + project["end_time"], "%Y-%m-%d"
                )
            if start_time <= datetime.now() <= end_time:
                msg += (
                    f'{project["project_name"]}\n'
                    f'开始时间: {start_time.strftime("%Y年%m月%d日")}\n'
                    f'结束时间: {end_time.strftime("%Y年%m月%d日")}\n'
                )
                if not state.get("official_qq", False):
                    msg += f'链接: https://show.bilibili.com/platform/detail.html?id={project["id"]}\n'
                msg += "\n"
        await bilibili_projects_matcher.finish(msg)
