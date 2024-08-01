from time import time
from datetime import datetime
import random

PRECISION = 0.1
START_TIME = int(
    datetime.strptime("2024-08-01T00:00:00", "%Y-%m-%dT%H:%M:%S").timestamp()
    / PRECISION
)
MACHINE_ID = sum(map(ord, "canrotbot")) % (2 << 10)


def generate_id():
    timestamp = int(time() / PRECISION) - START_TIME
    return (
        (1 << 62)
        + (timestamp << 22)
        + (MACHINE_ID << 12)
        + random.randint(0, (2 << 11))
    )
