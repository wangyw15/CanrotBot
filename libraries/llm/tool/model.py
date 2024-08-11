from typing import TypedDict, Literal, NotRequired, Any


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
    type: Literal["function"]
    function: ToolFunction


class ToolCallFunction(TypedDict):
    name: str
    arguments: NotRequired[dict[str, Any]]


class ToolCall(TypedDict):
    id: NotRequired[str]
    function: ToolCallFunction
    type: NotRequired[Literal["function"]]


class ToolCallResult(TypedDict):
    name: str
    tool_call_id: NotRequired[str]
    result: NotRequired[str]
    # message: NotRequired[UniMessage]
