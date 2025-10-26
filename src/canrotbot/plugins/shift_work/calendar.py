from datetime import datetime, timedelta

import icalendar

from .model import T_Cycles


def generate_calendar(
    cycles: T_Cycles, start_date: datetime, end_date: datetime
) -> icalendar.Calendar:
    cal = icalendar.Calendar()

    current_date = start_date
    while current_date <= end_date:
        current_period = cycles[(current_date - start_date).days % len(cycles)]
        if current_period is not None:
            name = current_period.name
            start_time = current_period.start
            end_time = current_period.end

            if start_time < end_time:
                start_time = datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    start_time.hour,
                    start_time.minute,
                )
                end_time = datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    end_time.hour,
                    end_time.minute,
                )
            else:
                start_time = datetime(
                    current_date.year,
                    current_date.month,
                    current_date.day,
                    start_time.hour,
                    start_time.minute,
                )
                next_day = current_date + timedelta(days=1)
                end_time = datetime(
                    next_day.year,
                    next_day.month,
                    next_day.day,
                    end_time.hour,
                    end_time.minute,
                )

            event = icalendar.Event()
            event.start = start_time
            event.end = end_time
            event.add("summary", name)

            cal.add_component(event)

        # bump date and cycle
        current_date += timedelta(days=1)

    return cal
