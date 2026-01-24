import subprocess
import sys

from nonebot import get_plugin_config

from canrotbot.llm.tools import register_tool
from .config import CalculatorConfig

_calculate_config = get_plugin_config(CalculatorConfig)


def qalc(expression: str) -> str:
    raw_result = subprocess.check_output(
        [_calculate_config.qalculate_bin, expression], shell=sys.platform == "win32"
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


@register_tool()
def calculate(expression: str) -> str:
    """
    Calcualte the given expression with qalculate
    All common operators — arithmetic, logical, bitwise, element-wise, (in)equalities
    Expressions may contain any combination of numbers, constants, functions, units, variables, matrices, vectors, and time/dates

    Args:
        expression: Expression
    
    Returns:
        Calculation result
    """
    return qalc(expression).strip()
