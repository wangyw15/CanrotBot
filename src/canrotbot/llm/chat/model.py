from dataclasses import dataclass

from langchain.agents.middleware import ModelRequest, dynamic_prompt
from nonebot import get_plugin_config

from ..config import LLMConfig

global_config = get_plugin_config(LLMConfig)


@dataclass
class ChatContext:
    private_chat: bool
    channel_chat: bool
    self_id: str | None
    platform_id: str
    user_id: int
    name: str


@dynamic_prompt
def context_aware_system_prompt(request: ModelRequest) -> str:
    prompt = global_config.system_prompt

    context: ChatContext | None = request.runtime.context  # type: ignore
    if context:
        if context.private_chat:
            prompt += "\nThe user is in a private chat"
        elif context.channel_chat:
            prompt += "\nThe user is in a channel chat"
        else:
            prompt += "\nThe user is in a group chat"

        prompt += f"\nThe platform specified id of the chat is {context.platform_id}, it may be the user's id or group id"
        prompt += f"\nThe user id of the user is {context.platform_id}"
        prompt += f"\nThe id of the assistant is {context.self_id}"

        if context.name:
            prompt += f"\nThe name of the user is {context.name}"

    return prompt
