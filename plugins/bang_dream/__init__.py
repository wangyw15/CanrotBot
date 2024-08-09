import difflib
import random

from arclet.alconna import Args, Subcommand, CommandMeta
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import (
    on_alconna,
    Alconna,
    Query,
    UniMessage,
    Text,
    Image,
    Voice,
)

from essentials.libraries import economy, user
from essentials.libraries import util
from . import bestdori, data, gacha_helper
from .config import BangDreamConfig

# TODO 记得改；模拟抽卡、查卡、点歌、签到主题、活动助手等

bang_dream_alconna = Alconna(
    "bang_dream",
    Subcommand(
        "comic",
        Args["comic_query", str, "random"],
        alias=["漫画", "小漫画", "四格", "单格"],
        help_text="随机小漫画",
    ),
    Subcommand(
        "song",
        Args["song_query", str, "random"],
        alias=["歌曲", "查歌", "查曲"],
        help_text="查游戏内歌曲",
    ),
    Subcommand(
        "gacha",
        Args["gacha_id", int],
        alias=["抽卡", "十连"],
        help_text="模拟十连",
    ),
    meta=CommandMeta(description="有关邦邦手游的功能"),
)

__plugin_meta__ = PluginMetadata(
    name="Bang Dream",
    description=bang_dream_alconna.meta.description,
    usage=bang_dream_alconna.get_help(),
    config=BangDreamConfig,
)

bang_dream_command = on_alconna(
    bang_dream_alconna,
    aliases={"bangdream", "邦邦"},
    block=True,
)

config = get_plugin_config(BangDreamConfig)


@bang_dream_command.assign("comic")
async def _(comic_query: Query[str] = Query("comic_query", "random")):
    comic_query = comic_query.result.strip()
    comics = await bestdori.comic.get_comic_list()
    comic_id = None
    if comic_query == "random":
        comic_id = random.choice(list(comics.keys()))
    elif comic_query == "单格":
        comic_id = random.choice([i for i in comics if len(i) == 3])
    elif comic_query == "四格":
        comic_id = random.choice(
            [i for i in comics if len(i) == 4 and i.startswith("1")]
        )
    elif comic_query.isdigit() and comic_query in comics:
        comic_id = comic_query
    else:
        best_match = 0.0
        for _comic_id, comic in comics.items():
            for _title in comic["title"]:
                ratio = difflib.SequenceMatcher(
                    None, comic_query, str(_title)
                ).quick_ratio()
                if ratio > best_match:
                    best_match = ratio
                    comic_id = _comic_id
    if comic_id is None or comic_id not in comics:
        await bang_dream_command.finish("没有找到这个漫画喵")
    title, _ = bestdori.util.get_content_by_language(
        comics[comic_id]["title"], config.default_language
    )
    msg = UniMessage()
    msg.append(Text(title))
    if await util.can_send_segment(Image):
        result = await bestdori.comic.get_comic(comic_id, config.default_language)
        msg.append(Image(raw=result[0]))
    else:
        msg.append(Text(f"\nhttps://bestdori.com/info/comics/{comic_id}"))
    await bang_dream_command.finish(msg)


@bang_dream_command.assign("song")
async def _(song_query: Query[str] = Query("song_query", "random")):
    song_query = song_query.result.strip()
    songs = await bestdori.song.get_song_list()
    song_id = None
    if song_query == "random":
        song_id = random.choice(list(songs.keys()))
    elif song_query.isdigit() and song_query in songs:
        song_id = song_query
    else:
        best_match = 0.0
        for _song_id, song in songs.items():
            for _title in song["musicTitle"]:
                ratio = difflib.SequenceMatcher(
                    None, song_query, str(_title)
                ).quick_ratio()
                if ratio > best_match:
                    best_match = ratio
                    song_id = _song_id
    if song_id is None or song_id not in songs:
        await bang_dream_command.finish("没有找到这首歌喵")
    info = await bestdori.song.get_song_info(song_id)
    # TODO 封面（难做
    await bang_dream_command.send(
        f'{bestdori.util.get_content_by_language(info["musicTitle"], config.default_language)[0]}\n'
        f'作词：{bestdori.util.get_content_by_language(info["lyricist"], config.default_language)[0]}\n'
        f'作曲：{bestdori.util.get_content_by_language(info["composer"], config.default_language)[0]}\n'
        f'编曲：{bestdori.util.get_content_by_language(info["arranger"], config.default_language)[0]}\n'
        f"链接：https://bestdori.com/info/songs/{song_id}"
    )
    # 发送信息
    if await util.can_send_segment(Voice):
        await bang_dream_command.send(
            Voice(url=await bestdori.song.get_song_url(song_id))
        )
    await bang_dream_command.finish()


@bang_dream_command.assign("gacha")
async def _(gacha_id: Query[int] = Query("gacha_id")):
    # TODO 卡池列表
    uid = user.get_uid()
    if not uid:
        await bang_dream_command.finish("你还没有账号喵~")

    # 付钱
    if not economy.pay(uid, 25, "邦邦十连"):
        await bang_dream_command.finish("你的余额不足喵~")
    await bang_dream_command.send(
        "你的二十五个胡萝卜片我就收下了~\n一緒にキラキラドキドキしまう！"
    )

    # 抽卡
    gacha_data = await gacha_helper.gacha10(gacha_id.result, config.default_language)

    # 保存结果
    gacha_helper.save_gacha_history(
        uid, gacha_id.result, gacha_data, config.default_language
    )

    # 发送信息
    msg = UniMessage()
    # 卡池信息
    msg.append(
        Text(
            await gacha_helper.get_gacha_name(gacha_id.result, config.default_language)
            + "\n"
        )
    )
    # 抽卡结果
    msg.append(
        Text(await gacha_helper.generate_text(gacha_data, config.default_language))
    )
    if await util.can_send_segment(Image):
        msg.append(Image(raw=await gacha_helper.generate_image(gacha_data)))
    await bang_dream_command.finish(msg)


@bang_dream_command.handle()
async def _():
    await bang_dream_command.finish(bang_dream_alconna.get_help())
