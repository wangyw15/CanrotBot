from datetime import datetime
from typing import NamedTuple


class CyclePeriod(NamedTuple):
    name: str
    start: datetime
    end: datetime


T_Cycles = list[CyclePeriod | None]
