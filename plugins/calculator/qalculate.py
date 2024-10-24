import subprocess

from nonebot import get_plugin_config

from .config import CalculatorConfig

_calculate_config = get_plugin_config(CalculatorConfig)


def qalc(expression: str) -> str:
    raw_result = subprocess.check_output(
        [_calculate_config.qalculate_bin, expression], shell=True
    )
    try:
        return raw_result.decode("utf-8")
    except UnicodeDecodeError:
        return raw_result.decode("gbk")


def get_version() -> str:
    return qalc("--version")


def check_qalculate() -> bool:
    try:
        get_version()
        return True
    except subprocess.CalledProcessError:
        return False


def calculate(expression: str) -> str:
    return qalc(expression).strip()
