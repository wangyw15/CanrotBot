from typing import Literal, TypedDict, NotRequired

from canrotbot.libraries.llm.tool.model import ToolCall


class Message(TypedDict):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    tool_calls: NotRequired[list[ToolCall]]
