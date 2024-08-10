from typing import Sequence

import openai
from nonebot import get_plugin_config
from nonebot_plugin_alconna import UniMessage

from .config import OpenAIConfig
from ... import tool
from ...model import Message

openai_config = get_plugin_config(OpenAIConfig)
openai_client = openai.AsyncOpenAI(
    base_url=openai_config.base_url, api_key=openai_config.api_key
)


async def chat(message: Sequence[Message] | str) -> tuple[str, UniMessage]:
    """
    生成聊天回复

    :param message: 消息

    :return: 返回消息，额外消息（可能为空消息）
    """
    extra_message: UniMessage = UniMessage()
    if isinstance(message, str):
        messages: list[Message] = [{"role": "user", "content": message}]
    else:
        messages = [i.copy() for i in message]

    response = await openai_client.chat.completions.create(
        model=openai_config.model,
        messages=messages,
        stream=False,
        tools=tool.tools_description,
    )

    if "tool_calls" in response["message"]:
        messages.append(response["message"])
        tool_results = tool.run_tool_call(response["message"]["tool_calls"])
        with_tool_call_result = False
        for result in tool_results:
            if "result" in result:
                with_tool_call_result = True
                messages.append({"role": "tool", "content": result["result"]})
            if "message" in result:
                extra_message += result["message"]

        if with_tool_call_result:
            response = await openai_client.chat.completions.create(
                model=openai_config.model,
                messages=messages,
                stream=False,
            )

    return response["message"]["content"], extra_message
