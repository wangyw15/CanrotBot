import abc
from typing import Any, Literal, Optional

from nonebot_plugin_alconna import UniMessage
from pydantic import BaseModel

type ToolType = Literal["function", "builtin_function"]


class Property(BaseModel):
    type: Literal["string"]
    description: str


class Parameters(BaseModel):
    type: Literal["object"]
    properties: dict[str, Property]
    required: list[str]


class ToolFunction(BaseModel):
    name: str
    description: str
    parameters: Parameters


class Tool(BaseModel):
    type: ToolType
    function: ToolFunction


class ToolCallFunction(BaseModel):
    name: str
    arguments: Optional[dict[str, Any]]


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


class ToolCallResult:
    name: str
    tool_call_id: Optional[str]
    result: Optional[str]
    instance: BaseTool

    def __init__(
        self,
        name: str,
        instance: BaseTool,
        tool_call_id: str = None,
        result: str = None,
    ):
        self.name = name
        self.instance = instance
        self.tool_call_id = tool_call_id
        self.result = result
