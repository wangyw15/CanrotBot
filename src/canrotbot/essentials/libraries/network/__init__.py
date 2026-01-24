from typing import Any

from httpx import AsyncClient
from nonebot import get_plugin_config, logger

from .config import NetworkConfig

network_config = get_plugin_config(NetworkConfig)

client = AsyncClient(timeout=network_config.timeout)
proxy_client: AsyncClient | None = None
if network_config.proxy:
    proxy_client = AsyncClient(
        proxy=network_config.proxy, timeout=network_config.timeout
    )


def get_client(use_proxy: bool = network_config.proxy != "") -> AsyncClient:
    """
    获取 httpx.AsyncClient

    :param use_proxy: 是否使用代理

    :return: httpx.AsyncClient
    """
    if use_proxy:
        if network_config.proxy != "" and proxy_client is not None:
            return proxy_client
        else:
            # raise ValueError("use_proxy is true but proxy not configured")
            logger.warning("use_proxy is true but proxy not configured")
    return client


async def fetch_bytes_data(
    url: str,
    *args,
    use_proxy: bool = network_config.proxy != "",
    **kwargs,
) -> bytes | None:
    """
    从 URL 获取 bytes 数据

    :param url: URL
    :param use_proxy: 是否使用代理
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: bytes 数据
    """
    _client = get_client(use_proxy)
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(
    url: str,
    *args,
    use_proxy: bool = network_config.proxy != "",
    **kwargs,
) -> Any | None:
    """
    从 URL 获取 json 数据

    :param url: URL
    :param use_proxy: 是否使用代理
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: json 数据
    """
    _client = get_client(use_proxy)
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def fetch_text_data(
    url: str,
    *args,
    use_proxy: bool = network_config.proxy != "",
    **kwargs,
) -> str | None:
    """
    从 URL 获取字符串

    :param url: URL
    :param use_proxy: 是否使用代理
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: 字符串
    """
    _client = get_client(use_proxy)
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.text
    return None
