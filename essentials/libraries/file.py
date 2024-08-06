import json
from os import PathLike
from pathlib import Path
from typing import Any


def read_text(path: str | Path | PathLike) -> str:
    """
    读取文本文件

    :param path: 文件路径

    :return: 文本数据
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_json(path: str | Path | PathLike) -> Any:
    """
    读取 JSON 文件

    :param path: 文件路径

    :return: JSON 数据
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_bytes(path: str | Path | PathLike) -> bytes:
    """
    读取二进制文件

    :param path: 文件路径

    :return: 二进制数据
    """
    with open(path, "rb") as f:
        return f.read()
