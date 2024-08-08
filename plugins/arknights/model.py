from enum import Enum
from typing import TypedDict, Literal


INDEX_TO_RARITY = [
    "one_star",
    "two_stars",
    "three_stars",
    "four_stars",
    "five_stars",
    "six_stars",
]


class OperatorProfessions(Enum):
    PIONEER = "PIONEER"
    WARRIOR = "WARRIOR"
    SNIPER = "SNIPER"
    CASTER = "CASTER"
    SUPPORT = "SUPPORT"
    MEDIC = "MEDIC"
    SPECIAL = "SPECIAL"
    TANK = "TANK"


class GachaOperatorData(TypedDict):
    id: str
    name: str
    rarity: Literal[0, 1, 2, 3, 4, 5]
    profession: Literal[
        "PIONEER", "WARRIOR", "SNIPER", "CASTER", "SUPPORT", "MEDIC", "SPECIAL", "TANK"
    ]


class GachaStatistics(TypedDict):
    user_id: int
    times: int
    one_star: int
    two_stars: int
    three_stars: int
    four_stars: int
    five_stars: int
    six_stars: int
    last_six_star: int
