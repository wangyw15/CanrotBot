from canrotbot.essentials.libraries.network import fetch_json_data
from canrotbot.llm.tools import register_tool

WEATHER_API = "https://aviationweather.gov/api/data/"


@register_tool()
async def metar(icao_codes: str | list[str]) -> None | list:
    """
    Retrive METAR data from Aviation Weather Center

    Args:
        icao_code: one ICAO code or a list of codes of the Airport(s)

    Returns:
        METAR report, None if failed
    """
    if isinstance(icao_codes, list):
        icao_codes = ",".join(icao_codes)
    return await fetch_json_data(
        WEATHER_API + "metar?ids=" + icao_codes + "&format=json"
    )


@register_tool()
async def taf(icao_codes: str | list[str], include_metar: bool = False) -> None | list:
    """
    Retrive TAF data from Aviation Weather Center

    Args:
        icao_code: one ICAO code or a list of codes of the Airport(s)
        include_metar: include METAR data

    Returns:
        TAF report, None if failed
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
