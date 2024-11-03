from typing import Any

from hishel import AsyncCacheClient, AsyncFileStorage
from httpx import AsyncClient
from nonebot import get_plugin_config, logger

from canrotbot.essentials.libraries import path

from .config import NetworkConfig

network_config = get_plugin_config(NetworkConfig)
cache_storage = AsyncFileStorage(
    base_path=path.get_cache_path(), ttl=network_config.cache_ttl or None
)

client = AsyncClient(timeout=network_config.timeout)
cache_client = AsyncCacheClient(storage=cache_storage, timeout=network_config.timeout)

if network_config.proxy:
    proxy_client = AsyncClient(
        proxy=network_config.proxy, timeout=network_config.timeout
    )
    proxy_cache_client = AsyncCacheClient(
        proxy=network_config.proxy,
        storage=cache_storage,
        timeout=network_config.timeout,
    )


def get_client(
    use_proxy: bool = network_config.proxy != "", use_cache: bool = False
) -> AsyncClient:
    """
    获取 httpx.AsyncClient

    :param use_proxy: 是否使用代理
    :param use_cache: 是否使用缓存

    :return: httpx.AsyncClient
    """
    if use_proxy:
        if network_config.proxy != "":
            return proxy_cache_client if use_cache else proxy_client
        else:
            # raise ValueError("use_proxy is true but proxy not configured")
            logger.warning("use_proxy is true but proxy not configured")
    return cache_client if use_cache else client


async def fetch_bytes_data(
    url: str,
    use_proxy: bool = network_config.proxy != "",
    use_cache: bool = False,
    *args,
    **kwargs,
) -> bytes | None:
    """
    从 URL 获取 bytes 数据

    :param url: URL
    :param use_proxy: 是否使用代理
    :param use_cache: 是否使用缓存
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: bytes 数据
    """
    _client = get_client(use_proxy, use_cache)
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(
    url: str,
    use_proxy: bool = network_config.proxy != "",
    use_cache: bool = False,
    *args,
    **kwargs,
) -> Any | None:
    """
    从 URL 获取 json 数据

    :param url: URL
    :param use_proxy: 是否使用代理
    :param use_cache: 是否使用缓存
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: json 数据
    """
    _client = get_client(use_proxy, use_cache)
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None


async def fetch_text_data(
    url: str,
    use_proxy: bool = network_config.proxy != "",
    use_cache: bool = False,
    *args,
    **kwargs,
) -> str | None:
    """
    从 URL 获取字符串

    :param url: URL
    :param use_proxy: 是否使用代理
    :param use_cache: 是否使用缓存
    :param args: 传递给 httpx.AsyncClient.get 的参数
    :param kwargs: 传递给 httpx.AsyncClient.get 的参数

    :return: 字符串
    """
    _client = get_client(use_proxy, use_cache)
    resp = await _client.get(url, *args, **kwargs)
    if resp.is_success and resp.status_code == 200:
        return resp.text
    return None
