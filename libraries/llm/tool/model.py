from typing import TypedDict, Literal, Mapping, Sequence, NotRequired, Any

from nonebot_plugin_alconna import UniMessage


class Property(TypedDict):
    type: Literal["string"]
    description: str


class Parameters(TypedDict):
    type: Literal["object"]
    properties: Mapping[str, Property]
    required: Sequence[str]


class ToolFunction(TypedDict):
    name: str
    description: str
    parameters: Parameters


class Tool(TypedDict):
    type: Literal["function"]
    function: ToolFunction


class ToolCallFunction(TypedDict):
    name: str
    arguments: NotRequired[Mapping[str, Any]]


class ToolCall(TypedDict):
    function: ToolCallFunction


class ToolCallResult(TypedDict):
    name: str
    result: NotRequired[str]
    message: NotRequired[UniMessage]
