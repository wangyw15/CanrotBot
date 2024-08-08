import ollama
from nonebot import get_plugin_config, logger
from nonebot_plugin_alconna import UniMessage
from ollama import Message

from .config import OllamaConfig
from ... import tool

ollama_config = get_plugin_config(OllamaConfig)
ollama_client = ollama.AsyncClient(ollama_config.ollama_host)


async def chat(text: str) -> str | UniMessage:
    messages: list[Message] = [{"role": "user", "content": text}]

    response = await ollama_client.chat(
        model=ollama_config.ollama_model,
        messages=messages,
        stream=False,
        tools=tool.tools_description + tool.custom_tools_description,
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
                messages.append({"role": "tool", "content": str(tool_ret)})
            elif tool_name in tool.custom_tools_callable:
                logger.info(f'Called custom tool "{tool_name}"')
                logger.debug(
                    f'Custom tool "{tool_name}" called with arguments {tool_args}'
                )
                tool_ret = tool.custom_tools_callable[tool_name](**tool_args)
                logger.debug(f'Custom tool "{tool_name}" returned with {tool_ret}')
                return tool_ret

        response = await ollama_client.chat(
            model=ollama_config.ollama_model,
            messages=messages,
            stream=False,
        )

    return response["message"]["content"]
