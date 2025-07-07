from canrotbot.essentials.libraries.network import fetch_json_data

WEATHER_API = "https://aviationweather.gov/api/data/"


async def metar(icao_codes: str | list[str]) -> None | list:
    """
    Retrive METAR data from Aviation Weather Center

    :params icao_code: one ICAO code or a list of codes

    :return: METAR data, None if failed
    """
    if isinstance(icao_codes, list):
        icao_codes = ",".join(icao_codes)
    return await fetch_json_data(
        WEATHER_API + "metar?ids=" + icao_codes + "&format=json"
    )


async def taf(icao_codes: str | list[str], include_metar: bool = False) -> None | list:
    """
    Retrive TAF data from Aviation Weather Center

    :params icao_code: one ICAO code or a list of codes
    :params include_metar: include METAR data

    :return: TAF data, None if failed
    """
    if isinstance(icao_codes, list):
        icao_codes = ",".join(icao_codes)
    return await fetch_json_data(
        WEATHER_API
        + "taf?ids="
        + icao_codes
        + "&format=json&metar="
        + str(include_metar).lower()
    )
