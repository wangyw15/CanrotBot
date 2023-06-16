from nonebot import logger
from pathlib import Path
import json
from typing import Any, Tuple


_random_text_assets_path = Path(__file__).parent.parent / 'assets/random_text'
_random_text_data: dict[str, list] = {}


def load_random_text_data() -> None:
    for i in _random_text_assets_path.glob('*.json'):
        with open(i, 'r', encoding='utf-8') as f:
            _random_text_data[i.stem] = json.load(f)
            logger.info(f'Random text loaded {i.stem}: {len(_random_text_data[i.stem])}')


load_random_text_data()


def get_data(name: str) -> list:
    return _random_text_data[name]
