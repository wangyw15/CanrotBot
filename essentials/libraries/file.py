import json
from os import PathLike
from pathlib import Path
from typing import Any


def read_json(path: str | Path | PathLike) -> Any:
    """
    读取 JSON 文件

    :param path: 文件路径

    :return: JSON 数据
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
