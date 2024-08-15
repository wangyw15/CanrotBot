import inspect

from nonebot import logger, get_driver
from nonebot_plugin_alconna import UniMessage

from .model import Tool, ToolCall, ToolCallResult, BaseTool


def resolve_tool(tool_provider: type[BaseTool]) -> Tool:
    """
    解析方法为 Tool 类型

    :param tool_provider: BaseTool 派生类

    :return: Tool
    """
    if not tool_provider.__description__:
        raise ValueError("Tool description must be provided")

    ret: Tool = {
        "type": "function",
        "function": {
            "name": tool_provider.__tool_name__ or tool_provider.__name__,
            "description": tool_provider.__description__,
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }

    tool_func = tool_provider.__call__
    signature = inspect.signature(tool_func)

    # 解析参数
    for param in signature.parameters.values():
        if param.name == "self":
            continue
        if param.annotation == inspect.Parameter.empty:
            raise ValueError(f"No type annotation found for argument {param.name}")
        if not isinstance(param.annotation.__metadata__[0], str):
            raise ValueError(
                f"Argument {param.name} must be annotated with str as description"
            )

        ret["function"]["parameters"]["properties"][param.name] = {
            "type": "string",
            "description": param.annotation.__metadata__[0],
        }
        ret["function"]["parameters"]["required"].append(param.name)

    # 检查返回值
    if signature.return_annotation != str:
        raise ValueError("Return value must be annotated as str")
    return ret


tools_description: list[Tool] = []
tools_callable: dict[str, type[BaseTool]] = {}


async def run_tool_call(tool_call: list[ToolCall]) -> list[ToolCallResult]:
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
            tool_instance = tools_callable[tool_name]()

            current_result = {"name": tool_name, "instance": tool_instance}

            logger.info(f'Tool "{tool_name}" called with arguments {tool_args}')
            tool_ret = await tool_instance(**tool_args)
            logger.info(
                f'Tool "{tool_name}" returned with {tool_ret[0:1000]}'  # 防止过长
                + f'{"..." if len(tool_ret) > 1000 else ""}'
            )

            # OpenAI 兼容
            if "id" in call:
                current_result["tool_call_id"] = call["id"]

            current_result["result"] = tool_ret
            ret.append(current_result)
        else:
            logger.warning(f'Tool "{call["function"]["name"]}" not found')
    return ret


async def run_message_postprocess(
    message: str, tool_results: list[ToolCallResult]
) -> UniMessage:
    ret_message = UniMessage(message)
    for tool in tool_results:
        ret_message = await tool["instance"].message_postprocess(ret_message)
    return ret_message


@get_driver().on_startup
async def register_tools():
    for tool_class in BaseTool.__subclasses__():
        tool = resolve_tool(tool_class)
        tools_description.append(tool)
        tools_callable[tool["function"]["name"]] = tool_class

        logger.info(
            f'Registered tool "{tool["function"]["name"]}" from "{tool_class.__name__}"'
        )
    logger.info(f"Registered {len(tools_description)} tools")


__all__ = [
    "BaseTool",
    "run_tool_call",
]
