from typing import Any

from nonebot import get_plugin_config
from .config import NetworkConfig

from httpx import AsyncClient

network_config = get_plugin_config(NetworkConfig)

if network_config.proxy:
    client = AsyncClient(proxy=network_config.proxy)
else:
    client = AsyncClient()
client.timeout = 10


async def fetch_bytes_data(url: str, *args, **kwargs) -> bytes | None:
    """
    从 URL 获取 bytes 数据

    :param url: URL
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: bytes 数据
    """
    resp = await client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(url: str, *args, **kwargs) -> Any | None:
    """
    从 URL 获取 json 数据

    :param url: URL
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: json 数据
    """
    resp = await client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def fetch_text_data(url: str, *args, **kwargs) -> str | None:
    """
    从 URL 获取字符串

    :param url: URL
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: 字符串
    """
    resp = await client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.text
    return None
