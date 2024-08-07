import inspect
from typing import Callable

from nonebot import logger, get_driver

from .model import Tool


def resolve_method(func: Callable) -> Tool:
    """
    解析方法为 Tool 类型

    :param func: 方法

    :return: Tool
    """
    docstring = inspect.getdoc(func) or ""
    if not docstring:
        raise ValueError("No docstring found")

    ret: Tool = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": "",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    lines = docstring.splitlines()
    for line in lines:
        if line.startswith(":param"):
            _, name, desc = line.split(" ", 2)
            name = name[:-1]
            ret["function"]["parameters"]["properties"][name] = {
                "type": "string",
                "description": desc,
            }
            ret["function"]["parameters"]["required"].append(name)
        elif line.startswith(":return"):
            _, desc = line.split(" ", 1)
        else:
            if line:
                ret["function"]["description"] += line + "\n"
    ret["function"]["description"] = ret["function"]["description"].strip()

    # 检查是否有缺失的描述
    if not ret["function"]["description"]:
        raise ValueError("No description found for function")

    for arg in inspect.getfullargspec(func).args:
        if (
            arg not in ret["function"]["parameters"]["properties"]
            or not ret["function"]["parameters"]["properties"][arg]["description"]
        ):
            raise ValueError(f"No description found for parameter {arg}")
    return ret


tools_description: list[Tool] = []
tools_callable: dict[str, Callable] = {}


def register_tool(func: Callable) -> Callable:
    """
    装饰器，将方法解析为 Tool 类型

    :param func: 方法

    :return: 方法
    """
    resolved = resolve_method(func)
    tools_description.append(resolved)
    tools_callable[resolved["function"]["name"]] = func
    logger.info(f"Registered tool \"{resolved['function']['name']}\"")
    return func


@get_driver().on_startup
async def log_tool_count():
    logger.info(f"Registered {len(tools_description)} tools")
