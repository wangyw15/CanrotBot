from typing import Optional, TypedDict


class Cloud(TypedDict):
    cover: str
    base: int


class METAR(TypedDict):
    metar_id: int
    icaoId: str
    receiptTime: str
    obsTime: int
    reportTime: str
    temp: int
    """Temperature"""
    dewp: int
    """Dew point"""
    wdir: int
    """Wind direction"""
    wspd: int
    """Wind speed"""
    wgst: Optional[int]
    visib: str
    """Visibility"""
    altim: int
    """Altimeter"""
    slp: Optional[int]
    qcField: int
    wxString: Optional[str]
    presTend: Optional[str]
    maxT: Optional[int]
    minT: Optional[int]
    maxT24: Optional[int]
    minT24: Optional[int]
    precip: Optional[int]
    pcp3hr: Optional[int]
    pcp6hr: Optional[int]
    pcp24hr: Optional[int]
    snow: Optional[str]
    vertVis: Optional[str]
    metarType: str
    rawOb: str
    mostRecent: int
    lat: float
    lon: float
    elev: int
    prior: int
    name: str
    clouds: list[Cloud]
