import json
from typing import cast

from nonebot import get_plugin_config
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
from openai.types.chat.chat_completion import ChatCompletion, Choice

from .config import OpenAIConfig
from ... import tool
from ...model import Message

openai_config = get_plugin_config(OpenAIConfig)
openai_client = AsyncOpenAI(
    base_url=openai_config.base_url, api_key=openai_config.api_key
)


def convert_tool_calls(
    openai_tool_calls: list[ChatCompletionMessageToolCall],
) -> list[tool.ToolCall]:
    ret: list[tool.ToolCall] = []
    for tool_call in openai_tool_calls:
        func = tool_call.function
        ret.append(
            {
                "id": tool_call.id,
                "function": {
                    "name": func.name,
                    "arguments": json.loads(func.arguments),
                },
            }
        )
    return ret


async def chat(message: list[Message] | str) -> str:
    """
    生成聊天回复

    :param message: 消息

    :return: 返回消息，额外消息（可能为空消息）
    """
    if isinstance(message, str):
        messages: list[ChatCompletionMessage] = [{"role": "user", "content": message}]
    else:
        messages: list[ChatCompletionMessage] = cast(
            list[ChatCompletionMessage], [i.copy() for i in message]
        )

    finish_reason: str | None = None
    choice: None | Choice = None

    while finish_reason is None or finish_reason == "tool_calls":
        completion: ChatCompletion = await openai_client.chat.completions.create(  # type: ignore
            model=openai_config.model,
            messages=messages,
            stream=False,
            tools=tool.tools_description,
        )

        choice = completion.choices[0]
        finish_reason = choice.finish_reason

        if finish_reason == "tool_calls":
            messages.append(choice.message)
            tool_calls = completion.choices[0].message.tool_calls or []

            tool_results = tool.run_tool_call(convert_tool_calls(tool_calls))
            for result in tool_results:
                messages.append(
                    cast(
                        ChatCompletionMessage,
                        {
                            "role": "tool",
                            "tool_call_id": result["tool_call_id"],
                            "name": result["name"],
                            "content": result["result"],
                        },
                    )
                )

    if choice:
        return choice.message.content
    return ""
