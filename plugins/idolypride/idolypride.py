import httpx
from datetime import datetime
import json


_client = httpx.AsyncClient()


async def get_full_calendar() -> list[dict]:
    resp = await _client.get('https://wiki.biligame.com/idolypride/api.php?action=expandtemplates&format=json&text=%7B%7B%23invoke%3A%E6%97%A5%E5%8E%86%E5%87%BD%E6%95%B0%7CgetAllData%7D%7D')
    if resp.is_success and resp.status_code == 200:
        data = resp.json()['expandtemplates']['*']
        # 处理csv
        table: list[list[str]] = [line.split(',') for line in data.split(';') if line]
        ret: list[dict] = []
        for row in table:
            ret.append({
                'start': datetime.strptime(row[0], '%Y/%m/%d'),
                'end': datetime.strptime(row[1], '%Y/%m/%d'),
                'name': row[2],
                'type': row[3],
                'page': row[4],
                'color': row[5]
            })
        return ret
    return []


async def get_today_events() -> list[dict]:
    data = await get_full_calendar()
    ret: list[dict] = []
    for i in data:
        if i['start'].date() <= datetime.now().date() <= i['end'].date():
            ret.append(i)
    return ret


async def main():
    data = await get_today_events()
    print(data)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
