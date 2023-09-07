import httpx
import typing

_client = httpx.AsyncClient()


async def get_thread_data(thread_number: str) -> typing.Any | None:
    """
    获取串号内容

    :param thread_number: 串号

    :return: 串的第一页内容
    """
    resp = await _client.get(f'https://api.nmb.best/api/thread?id={thread_number}&page=1')
    if resp.is_success and resp.status_code == 200:
        return resp.json()
    return None

__all__ = ['get_thread_data']
