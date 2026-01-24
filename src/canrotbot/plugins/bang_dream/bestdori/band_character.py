from typing import Any

from canrotbot.llm.tools import register_tool

from . import util


@register_tool("bang_dream_get_character_list")
async def get_character_list() -> dict[str, Any]:
    """
    Get character list from Bang Dream

    Returns:
        Character list in JSON format
    """
    return await util.bestdori_api("characters/main.3.json")


@register_tool("bang_dream_get_character_info")
async def get_character_info(character_id: str) -> dict[str, Any]:
    """
    Get character information from Bang Dream

    Args:
        character_id: Character ID for the character

    Returns:
        Character information in JSON format
    """
    return await util.bestdori_api(f"characters/{character_id}.json")


@register_tool("bang_dream_get_band_list")
async def get_band_list() -> dict[str, Any]:
    """
    Get Band list from Bang Dream

    Returns:
        Band list in JSON format
    """
    return await util.bestdori_api("bands/main.1.json")
