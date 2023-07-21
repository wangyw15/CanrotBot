import importlib
import pkgutil
from pathlib import Path

from nonebot import logger


def load_themes() -> None:
    """
    加载所有主题
    """
    for _, name, _ in pkgutil.iter_modules([str(Path(__file__).parent)]):
        if not name.startswith('_'):
            importlib.import_module(f'{__name__}.{name}')
            logger.info(f'Loaded fortune theme plugin: {name}')
