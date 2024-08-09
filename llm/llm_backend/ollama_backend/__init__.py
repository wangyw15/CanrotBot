import inspect
from typing import overload

import ollama
from nonebot import get_plugin_config, logger
from nonebot_plugin_alconna import UniMessage
from ollama import Message

from .config import OllamaConfig
from ... import tool

ollama_config = get_plugin_config(OllamaConfig)
ollama_client = ollama.AsyncClient(ollama_config.ollama_host)


async def chat(message: list[Message] | str) -> str | UniMessage:
    extra_message: UniMessage = UniMessage()
    if isinstance(message, str):
        messages: list[Message] = [{"role": "user", "content": message}]
    else:
        messages = [i.copy() for i in message]

    response = await ollama_client.chat(
        model=ollama_config.ollama_model,
        messages=messages,
        stream=False,
        tools=tool.tools_description,
    )

    if "tool_calls" in response["message"]:
        messages.append(response["message"])
        for tool_call in response["message"]["tool_calls"]:
            tool_name: str = tool_call["function"]["name"]
            tool_args: dict = tool_call["function"]["arguments"]

            if tool_name in tool.tools_callable:
                logger.info(f'Called tool "{tool_name}"')
                logger.debug(f'Tool "{tool_name}" called with arguments {tool_args}')

                tool_ret = tool.tools_callable[tool_name](**tool_args)
                logger.debug(f'Tool "{tool_name}" returned with {tool_ret}')

                return_type = inspect.signature(
                    tool.tools_callable[tool_name]
                ).return_annotation
                if return_type == UniMessage:
                    return tool_ret
                elif return_type == tuple[str, UniMessage]:
                    extra_message.append(tool_ret[1])
                    tool_ret = tool_ret[0]
                elif return_type == tuple[UniMessage | str]:
                    extra_message.append(tool_ret[0])
                    tool_ret = tool_ret[1]

                messages.append({"role": "tool", "content": str(tool_ret)})

        response = await ollama_client.chat(
            model=ollama_config.ollama_model,
            messages=messages,
            stream=False,
        )

    if len(extra_message) > 0:
        return UniMessage.text(response["message"]["content"]) + extra_message
    return response["message"]["content"]
