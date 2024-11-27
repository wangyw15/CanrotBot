import abc
from typing import Any, Literal, NotRequired, TypedDict

from nonebot_plugin_alconna import UniMessage

type ToolType = Literal["function", "builtin_function"]


class Property(TypedDict):
    type: Literal["string"]
    description: str


class Parameters(TypedDict):
    type: Literal["object"]
    properties: dict[str, Property]
    required: list[str]


class ToolFunction(TypedDict):
    name: str
    description: str
    parameters: Parameters


class Tool(TypedDict):
    type: ToolType
    function: ToolFunction


class ToolCallFunction(TypedDict):
    name: str
    arguments: NotRequired[dict[str, Any]]


class ToolCall(TypedDict):
    id: NotRequired[str]
    function: ToolCallFunction
    type: NotRequired[Literal["function"]]


class BaseTool(metaclass=abc.ABCMeta):
    __tool_type__: ToolType = "function"
    """ Tool 类型 """
    __tool_name__: str = ""
    """ Tool 名称 """
    __description__: str = ""
    """ Tool 描述 """
    __command__: bool = False
    """ 是否是命令，如果是命令则会阻断 llm 后续对话，直接调用 tool_call """

    @abc.abstractmethod
    async def __call__(self, *args, **kwargs) -> str:
        """
        tool_call 调用的方法
        """
        pass

    async def message_postprocess(self, message: UniMessage) -> UniMessage:
        """
        对 tool_call 的返回结果进行后处理，根据 tool_call 调用顺序执行

        :param message: 上一个 message_postprocess 处理后的 UniMessage

        :return: 返回处理后的 UniMessage
        """
        return message


class ToolCallResult(TypedDict):
    name: str
    tool_call_id: NotRequired[str]
    result: NotRequired[str]
    instance: BaseTool
