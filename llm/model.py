from typing import Literal, TypedDict


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
