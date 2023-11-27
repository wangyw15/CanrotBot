from pathlib import Path

from nonebot import load_plugins
from storage import asset

_random_text_assets_path = (
    Path(__file__).parent.parent.parent / "assets" / "random_text"
)
_random_text_data = asset.Asset("random_text")


def get_data(name: str) -> list:
    return _random_text_data[name]


load_plugins(str(Path(__file__).parent))
