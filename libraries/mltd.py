from ..adapters import unified
from typing import Literal
from datetime import datetime


async def get_events(time: Literal['now'] | datetime = 'now') -> list[dict] | None:
    if time == 'now':
        return await unified.util.fetch_json_data(f'https://api.matsurihi.me/api/mltd/v2/events?at=now')
    elif isinstance(time, datetime):
        t = datetime.now().astimezone().replace(microsecond=0).isoformat()
        return await unified.util.fetch_json_data(f'https://api.matsurihi.me/api/mltd/v2/events?at={t}')
