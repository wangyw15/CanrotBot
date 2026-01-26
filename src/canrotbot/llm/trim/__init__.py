from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime

from .config import TrimConfig


def trim_messages(keep: int):
    @before_model
    def _trim(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        messages = state["messages"]

        if len(messages) <= keep:
            return None

        return {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                messages[0],
                *messages[-keep:],
            ]
        }

    return _trim


__all__ = [
    "trim_messages",
    "TrimConfig",
]
