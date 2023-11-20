from httpx import AsyncClient
import typing

_client = AsyncClient()


async def get_station_list(longitude: float | str, latitude: float | str) -> list[dict[str, typing.Any]]:
    resp = await _client.get(
        f'https://api.issks.com/issksapi/V2/ec/stationList/json.shtml?mapX={longitude}&mapY={latitude}')
    if resp.is_success and resp.status_code == 200:
        return resp.json()['list']
    return []


async def get_station_plugs(station_id: int) -> list[dict[str, typing.Any]]:
    resp = await _client.get(f'https://api.issks.com/issksapi/V2/ec/chargingList.shtml?stationId={station_id}')
    if resp.is_success and resp.status_code == 200:
        return resp.json()['list']
    return []


async def generate_message(stations: list[dict[str, typing.Any]], keyword: str = '') -> str:
    ret = ''
    for station in stations:
        if station['iHardWareState'] != 1 or keyword and keyword not in station['vStationName']:
            continue
        plugs = await get_station_plugs(station['iStationId'])
        if plugs:
            ret += f'{station["vStationName"]}: {len(plugs)}\n'
    return ret


async def main() -> None:
    pass

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

__all__ = ['get_station_list', 'get_station_plugs', 'generate_message']
