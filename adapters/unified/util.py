from nonebot import get_driver
from typing import Any
import httpx


_driver = get_driver()
_global_config = _driver.config


def get_config(name: str) -> Any:
    return _global_config.dict()[name]


if proxy := get_config('canrot_proxy'):
    _client = httpx.AsyncClient(proxies=proxy)
else:
    _client = httpx.AsyncClient()
_client.timeout = 10


async def fetch_bytes_data(url: str) -> bytes | None:
    """从URL获取bytes数据"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.content
    return None


async def fetch_json_data(url: str) -> dict | None:
    """从URL获取json数据"""
    resp = await _client.get(url)
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None