from datetime import datetime

from .model import CyclePeriod, T_Cycles

T_RawCycles = list[tuple[str, str, str] | list[str] | None]


def parse_time(time_str: str):
    time_format = [
        "%H:%M",
        "%H%M",
    ]

    for i in time_format:
        try:
            return datetime.strptime(time_str, i)
        except ValueError:
            continue


def parse_date(date_str: str) -> datetime | None:
    date_format = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%Y%m%d",
    ]

    for i in date_format:
        try:
            return datetime.strptime(date_str, i)
        except ValueError:
            continue


def parse_cycles(raw_cycles: T_RawCycles) -> T_Cycles:
    cycles: T_Cycles = []

    for i in raw_cycles:
        if i is None:
            cycles.append(None)
        else:
            name, start_str, end_str = i

            start_time = parse_time(start_str)
            end_time = parse_time(end_str)

            if start_time is None:
                raise ValueError(f"Cannot parse start time: {start_str}")
            if end_time is None:
                raise ValueError(f"Cannot parse end time: {end_str}")

            cycles.append(
                CyclePeriod(
                    name,
                    start_time,
                    end_time,
                )
            )

    return cycles
