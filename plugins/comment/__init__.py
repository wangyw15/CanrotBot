from datetime import datetime, timezone, timedelta

from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg, Arg
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State
from sqlalchemy import select, insert

from essentials.libraries import user
from libraries import anime
from storage import database
from . import data

__plugin_meta__ = PluginMetadata(
    name="锐评记录",
    description="记录各种锐评",
    usage="懒得写",
    config=None,  # TODO 帮助信息
)

_anime_comment_add_handler = on_command("评价番剧", aliases={"锐评番剧"}, block=True)


@_anime_comment_add_handler.handle()
async def _(state: T_State, args: Message = CommandArg()):
    if anime_name := args.extract_plain_text():
        name, anilist_id, _ = anime.search_anilist_id_by_name(anime_name)
        if anilist_id:
            anilist_id = str(anilist_id)
            state["anilist_id"] = anilist_id
            await _anime_comment_add_handler.send(
                f'对"{name}"开始一段锐评，stop则不添加评价'
            )
        else:
            await _anime_comment_add_handler.finish("AniList 中不存在这部番剧")
    else:
        await _anime_comment_add_handler.finish("未输入番剧名称")


@_anime_comment_add_handler.got("comment_msg")
async def _(state: T_State, comment_msg: Message = Arg()):
    uid = user.get_uid()
    if comment := comment_msg.extract_plain_text():
        if comment.strip() == "stop":
            await _anime_comment_add_handler.finish("未添加评价")
        with database.get_session().begin() as session:
            session.execute(
                insert(data.Comment).values(
                    user_id=uid,
                    type=data.CommentType.anime,
                    time=datetime.now(timezone(timedelta(hours=8))),
                    title=state["anilist_id"],
                    content=comment,
                    nickname=await user.get_user_name(default="anonymous"),
                )
            )
            session.commit()
        await _anime_comment_add_handler.finish("锐评已保存")


_anime_comment_view_handler = on_command(
    "查看番剧锐评", aliases={"查看番剧评价"}, block=True
)


@_anime_comment_view_handler.handle()
async def _(args: Message = CommandArg()):
    if anime_name := args.extract_plain_text():
        name, anilist_id, _ = anime.search_anilist_id_by_name(anime_name)
        if anilist_id:
            anilist_id = str(anilist_id)
            with database.get_session().begin() as session:
                _comment_data = (
                    session.execute(
                        select(data.Comment).where(
                            data.Comment.type.is_(data.CommentType.anime),
                            data.Comment.title.is_(anilist_id),
                        )
                    )
                    .scalars()
                    .all()
                )
                all_comments = ""
                for i in _comment_data:
                    all_comments += (
                        f"{i.time.strftime('%Y/%m/%d %H:%M:%S')} - "
                        f"{i.nickname}\n"
                        f"{i.content}\n\n"
                    )
                await _anime_comment_view_handler.finish(all_comments.strip())
        else:
            await _anime_comment_add_handler.finish("AniList 中不存在这部番剧")
    else:
        await _anime_comment_add_handler.finish("未输入番剧名称")
