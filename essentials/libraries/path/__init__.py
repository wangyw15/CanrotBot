from pathlib import Path

from nonebot import get_plugin_config

from .config import FileConfig

config = get_plugin_config(FileConfig)


def get_asset_path(name: str = "") -> Path:
    """
    获取资源文件夹路径

    :param name: 资源文件夹名，如果为空则返回 asset 目录

    :return: 文件夹路径
    """
    path = Path(__file__).parent.parent.parent.parent / "assets" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_path(name: str = "") -> Path:
    """
    获取缓存文件夹路径

    :param name: 缓存文件夹名

    :return: 文件夹路径
    """
    path = Path(config.user_data_path) / "cache" / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_data_path(name: str) -> Path:
    """
    获取数据文件夹路径

    :param name: 数据文件夹名

    :return: 文件夹路径
    """
    path = Path(config.user_data_path) / "data" / name
    path.mkdir(parents=True, exist_ok=True)
    return path
