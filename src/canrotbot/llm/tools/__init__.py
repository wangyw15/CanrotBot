from typing import Callable

from langchain.tools import BaseTool, tool

_tools: list[BaseTool] = []


def register_tool(*args, **kwargs) -> Callable:
    def _append_tool(func: Callable) -> Callable:
        _tools.append(tool(*args, **kwargs)(func))
        return func

    return _append_tool


def get_tools() -> list[BaseTool]:
    return _tools
