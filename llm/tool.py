import inspect
from typing import Callable

from nonebot import logger, get_driver
from nonebot_plugin_alconna import UniMessage

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

custom_tools_description: list[Tool] = []
custom_tools_callable: dict[str, Callable] = {}


def check_annotation(func: Callable, return_type: type) -> bool:
    """
    检查方法参数是否全部标记为 str，是否有返回值标注

    :param func: 方法
    :param return_type: 返回值类型

    :return: 是否通过检查
    """
    spec = inspect.getfullargspec(func)
    for arg in spec.args:
        if arg not in spec.annotations:
            raise ValueError(f"No type annotation found for argument {arg}")
        if spec.annotations[arg] is not str:
            raise ValueError(f"Argument {arg} must be annotated as str")
    if "return" not in spec.annotations:
        raise ValueError("No type annotation found for return")
    if spec.annotations["return"] is not return_type:
        raise ValueError(f"Return value must be annotated as {return_type.__name__}")
    return True


def register_tool(func: Callable) -> Callable:
    """
    装饰器，将方法注册为 Tool，需要参数和返回值都标记为 str

    :param func: 方法

    :return: 方法
    """
    # 检查类型标注
    if not check_annotation(func, str):
        raise ValueError("Annotation check failed")

    # 注册 Tool
    resolved = resolve_method(func)
    tools_description.append(resolved)
    tools_callable[resolved["function"]["name"]] = func
    logger.info(f"Registered tool \"{resolved['function']['name']}\"")
    return func


def register_custom_tool(func: Callable) -> Callable:
    """
    装饰器，将方法注册为 Tool，且返回消息由 Tool 自定义，需要参数标记为 str，返回标记为 UniMessage

    :param func: 方法

    :return: 方法
    """
    # 检查类型标注
    if not check_annotation(func, UniMessage):
        raise ValueError("Annotation check failed")

    # 注册 Custom tool
    resolved = resolve_method(func)
    custom_tools_description.append(resolved)
    custom_tools_callable[resolved["function"]["name"]] = func
    logger.info(f"Registered custom tool \"{resolved['function']['name']}\"")
    return func


@get_driver().on_startup
async def log_tool_count():
    logger.info(f"Registered {len(tools_description)} tools")
    logger.info(f"Registered {len(custom_tools_description)} custom tools")
