from typing import Any, NamedTuple, Optional, TypedDict


class Effects(TypedDict):
    """
    宝可梦攻击额外效果
    """

    effectiveness: Optional[float]


class EvalResult(NamedTuple):
    """
    运行Poky语言的结果
    """

    result: Any
    stack: list[Any]
    effects: Effects
