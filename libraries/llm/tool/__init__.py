import inspect
from typing import Callable

from nonebot import logger, get_driver

from .model import Tool, ToolCall, ToolCallResult


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


def check_annotation(func: Callable) -> type:
    """
    检查方法参数是否全部标记为 str，是否有返回值标注

    :param func: 方法

    :return: 返回值类型
    """
    spec = inspect.getfullargspec(func)
    for arg in spec.args:
        if arg not in spec.annotations:
            raise ValueError(f"No type annotation found for argument {arg}")
        if spec.annotations[arg] is not str:
            raise ValueError(f"Argument {arg} must be annotated as str")
    if "return" not in spec.annotations:
        raise ValueError("No type annotation found for return")
    return spec.annotations["return"]


def register_tool(func: Callable) -> Callable:
    """
    装饰器，将方法注册为 Tool，需要参数和返回值都标记为 str

    :param func: 方法

    :return: 方法
    """
    # 检查类型标注
    if check_annotation(func) != str:
        raise ValueError("Tool function's return type must be str")

    # 注册 Tool
    resolved = resolve_method(func)
    tools_description.append(resolved)
    tools_callable[resolved["function"]["name"]] = func
    logger.info(f"Registered tool \"{resolved['function']['name']}\"")
    return func


def run_tool_call(tool_call: list[ToolCall]) -> list[ToolCallResult]:
    """
    执行 Tool

    :param tool_call: ToolCall

    :return: 返回值
    """
    ret: list[ToolCallResult] = []

    for call in tool_call:
        if call["function"]["name"] in tools_callable:
            tool_name = call["function"]["name"]
            tool_args = call["function"]["arguments"]

            logger.info(f'Tool "{tool_name}" called with arguments {tool_args}')
            tool_ret = tools_callable[tool_name](**tool_args)
            logger.info(f'Tool "{tool_name}" returned with {tool_ret}')

            # 生成返回值
            current_result = {"name": tool_name}

            # OpenAI 兼容
            if "id" in call:
                current_result["tool_call_id"] = call["id"]

            current_result["result"] = tool_ret
            ret.append(current_result)
        else:
            logger.warning(f'Tool "{call["function"]["name"]}" not found')
    return ret


@get_driver().on_startup
async def log_tool_count():
    logger.info(f"Registered {len(tools_description)} tools")


__all__ = [
    "register_tool",
    "run_tool_call",
]
