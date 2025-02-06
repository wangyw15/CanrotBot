import inspect
import json
from typing import cast

from nonebot import get_driver, get_plugin_config, logger
from nonebot_plugin_alconna import UniMessage
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)

from ..config import OpenAIConfig
from .model import (
    BaseTool,
    Parameters,
    Property,
    Tool,
    ToolCallResult,
    ToolFunction,
    ToolType,
)

openai_config = get_plugin_config(OpenAIConfig)


def resolve_tool(tool_provider: type[BaseTool]) -> Tool:
    """
    解析方法为 Tool 类型

    :param tool_provider: BaseTool 派生类

    :return: Tool
    """
    tool_type: ToolType = tool_provider.__tool_type__ or cast(ToolType, "function")

    ret: Tool = Tool(
        type=tool_type,
        function=ToolFunction(
            name=tool_provider.__tool_name__ or tool_provider.__name__,
            description=tool_provider.__description__,
            parameters=Parameters(type="object", properties={}, required=[]),
        ),
    )

    tool_func = tool_provider.__call__
    signature = inspect.signature(tool_func)

    # 检查返回值
    if signature.return_annotation != str:
        raise ValueError("Return value must be annotated as str")

    # builtin_function 忽略剩下的检查
    if tool_type == "builtin_function":
        return ret

    # 检查描述
    if not tool_provider.__description__:
        raise ValueError("Tool description must be provided")

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

        ret.function.parameters.properties[param.name] = Property(
            type="string",
            description=param.annotation.__metadata__[0],
        )
        ret.function.parameters.required.append(param.name)
    return ret


tools_description: list[Tool] = []
tools_callable: dict[str, type[BaseTool]] = {}


async def run_tool_call(
    tool_call: list[ChatCompletionMessageToolCall],
) -> list[ToolCallResult]:
    """
    执行 Tool

    :param tool_call: ToolCall

    :return: 返回值
    """
    ret: list[ToolCallResult] = []

    for call in tool_call:
        tool_name = call.function.name
        tool_args = json.loads(call.function.arguments)
        if call.function.name in tools_callable:
            tool_instance = tools_callable[tool_name]()

            current_result = ToolCallResult(name=tool_name, instance=tool_instance)

            logger.info(f'Tool "{tool_name}" called with arguments {tool_args}')
            tool_ret = await tool_instance(**tool_args)
            logger.info(
                f'Tool "{tool_name}" returned with {tool_ret[0:1000]}'  # 防止过长
                + f' {"..." if len(tool_ret) > 1000 else ""}'
            )

            current_result.tool_call_id = call.id
            current_result.result = tool_ret
            ret.append(current_result)
        else:
            logger.warning(f'Tool "{call.function.name}" not found')
    return ret


async def run_message_postprocess(
    message: str, tool_results: list[ToolCallResult]
) -> UniMessage:
    ret_message = UniMessage(message)
    for tool in tool_results:
        ret_message = await tool.instance.message_postprocess(ret_message)
    return ret_message


@get_driver().on_startup
async def register_tools():
    for tool_class in BaseTool.__subclasses__():
        # 非Moonshot不支持builtin_function
        if (
            tool_class.__tool_type__ == "builtin_function"
            and not openai_config.model.startswith("moonshot-")
        ):
            continue
        tool = resolve_tool(tool_class)
        tools_description.append(tool)
        tools_callable[tool.function.name] = tool_class

        logger.info(
            f'Registered tool "{tool.function.name}" from "{tool_class.__name__}"'
        )
    logger.info(f"Registered {len(tools_description)} tools")


__all__ = [
    "BaseTool",
    "run_tool_call",
]
