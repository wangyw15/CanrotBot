from typing import Literal, TypedDict, NotRequired, Sequence

from libraries.llm.tool.model import ToolCall


class Message(TypedDict):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    tool_calls: NotRequired[Sequence[ToolCall]]
