import json
import random
from typing import Literal

from nonebot import get_driver

from canrotbot.essentials.libraries import path

from ..data import get_pokemon_types, get_type_effectiveness
from ..poky import Effects, PokyMachine
from .model import Move

ASSET_PATH = path.get_asset_path("pokemon/type_challenge")

TYPES: list[str] = []
MOVES: dict[str, Move] = {}
TYPE_EFFECTIVENESS: dict[str, dict[str, float]] = {}
PROMPTS: dict[str, dict[str, str]] = {}


@get_driver().on_startup
async def _load_ptc_asset():
    global TYPES, MOVES, TYPE_EFFECTIVENESS, PROMPTS
    TYPES = get_pokemon_types()
    with (ASSET_PATH / "moves.json").open("r", encoding="utf-8") as f:
        MOVES = json.load(f)
    TYPE_EFFECTIVENESS = get_type_effectiveness()
    with (ASSET_PATH / "prompts.json").open("r", encoding="utf-8") as f:
        PROMPTS = json.load(f)


def generate_pokemon(mode: Literal["1", "2", "random"] = "random") -> list[str]:
    """
    根据模式生成宝可梦属性

    :param mode: 模式: "1": 生成一个属性; "2": 生成两个属性; "random": 随机生成一个或两个属性

    :return: 属性列表
    """
    if mode == "1":
        return random.sample(TYPES, 1)
    elif mode == "2":
        return random.sample(TYPES, 2)
    elif mode == "random":
        return random.sample(TYPES, random.randint(1, 2))
    else:
        raise ValueError("Invalid mode. Must be '1', '2' or 'random'.")


def calculate_effectiveness(attacker_type: str, defender_types: list[str]) -> float:
    """
    计算攻击方对防御方的属性克制效果

    :param attacker_type: 攻击方属性
    :param defender_types: 防御方属性列表

    :return: 属性克制效果
    """
    effectiveness = 1.0
    for defender_type in defender_types:
        effectiveness *= TYPE_EFFECTIVENESS[attacker_type][defender_type]
    return effectiveness


def get_effectiveness_prompt(multiplier: float) -> str:
    """
    根据属性克制效果获取提示信息

    :param multiplier: 属性克制效果

    :return: 提示信息
    """
    if multiplier == 0:
        return "没有效果！"
    if multiplier <= 0.5:
        return "效果不理想..."
    if multiplier < 2:
        return "效果一般"
    return "效果拔群！"


def check_type(_type: str) -> bool:
    """
    检查属性是否有效

    :param _type: 属性名称

    :return: 是否有效
    """
    return _type in TYPES


def check_move(move: str) -> bool:
    """
    检查技能是否有效

    :param move: 技能名称

    :return: 是否有效
    """
    return move in MOVES


def get_move_type(move: str, machine: PokyMachine) -> str:
    """
    获取技能属性

    :param move: 技能名称
    :param machine: PokyMachine实例

    :return: 属性
    """
    if check_move(move):
        return machine.eval(MOVES[move]["type"]).result
    return ""


def get_attack_prompt(attack: str, machine: PokyMachine) -> str:
    """
    获取技能提示信息

    :param attack: 属性或技能名称
    :param machine: PokyMachine实例

    :return: 提示信息
    """
    if check_move(attack):
        return machine.eval(MOVES[attack]["prompt"], {
            "prompts": PROMPTS
        }).result
    elif check_type(attack):
        return PROMPTS["attack"]["default"]
    return ""


def get_move_effects(move: str, machine: PokyMachine) -> Effects:
    """
    获取技能效果

    :param move: 技能名称
    :param machine: PokyMachine实例

    :return: 技能效果
    """
    if check_move(move):
        return machine.eval(MOVES[move]["effect"]).effects
    return {}


def compare_types(types1: list[str], types2: list[str]) -> bool:
    """
    比较两个属性列表

    :param types1: 属性列表1
    :param types2: 属性列表2

    :return: 是否相同
    """
    return sorted(types1) == sorted(types2)


def get_all_prompts() -> dict[str, dict[str, str]]:
    """
    获取所有提示信息

    :return: 提示信息字典
    """
    return PROMPTS
