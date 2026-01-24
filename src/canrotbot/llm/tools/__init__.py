from typing import Callable

from langchain.tools import BaseTool, tool

_tools: list[BaseTool] = []


def register_tool(func: Callable):
    _tool = tool(func)
    _tools.append(_tool)
    return _tool


def get_tools() -> list[BaseTool]:
    return _tools
