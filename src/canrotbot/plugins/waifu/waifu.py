from typing import Literal

from nonebot_plugin_alconna import UniMessage

from canrotbot.essentials.libraries.network import fetch_json_data
from canrotbot.llm.tools import register_tool

API_URL = "https://api.waifu.pics/{type}/{category}"
AVAILABLE_CATEGORY = [
    "waifu",
    "neko",
    "shinobu",
    "megumin",
    "bully",
    "cuddle",
    "cry",
    "hug",
    "awoo",
    "kiss",
    "lick",
    "pat",
    "smug",
    "bonk",
    "yeet",
    "blush",
    "smile",
    "wave",
    "highfive",
    "handhold",
    "nom",
    "bite",
    "glomp",
    "slap",
    "kill",
    "kick",
    "happy",
    "wink",
    "poke",
    "dance",
    "cringe",
]


async def get_waifu_url(
    image_type: Literal["sfw", "nsfw"], category: str
) -> str | None:
    data = await fetch_json_data(API_URL.format(type=image_type, category=category))
    if data is None:
        return None
    return data["url"]


@register_tool()
async def send_waifu_image(category: str = "waifu") -> str:
    """
    Send a random waifu image to the user.
    This tool will automatically send the image to the user, so there's no need to send it again in the response.

    Args:
        category: The image category, default is waifu, accept the following values:
            waifu, neko, shinobu, megumin, bully,
            cuddle, cry, hug, awoo, kiss,
            lick, pat, smug, bonk, yeet, blush,
            smile, wave, highfive, handhold, nom,
            bite, glomp, slap, kill, kick,
            happy, wink, poke, dance, cringe

    Returns:
        The URL of the image, empty if failed
    """
    if category not in AVAILABLE_CATEGORY:
        return ""

    url = await get_waifu_url("sfw", category)
    if not url:
        return ""

    await UniMessage.image(url=url).send()
    return url
