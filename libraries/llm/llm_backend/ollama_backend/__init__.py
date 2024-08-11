import ollama
from nonebot import get_plugin_config

from .config import OllamaConfig
from ... import tool
from ...model import Message

ollama_config = get_plugin_config(OllamaConfig)
ollama_client = ollama.AsyncClient(ollama_config.host)


async def chat(message: list[Message] | str) -> str:
    """
    生成聊天回复

    :param message: 消息

    :return: 返回消息，额外消息（可能为空消息）
    """
    if isinstance(message, str):
        messages: list[Message] = [{"role": "user", "content": message}]
    else:
        messages = [i.copy() for i in message]

    response = await ollama_client.chat(  # type: ignore
        model=ollama_config.model,
        messages=messages,
        stream=False,
        tools=tool.tools_description,
    )

    if "tool_calls" in response["message"]:
        messages.append(response["message"])

        tool_results = tool.run_tool_call(response["message"]["tool_calls"])
        for result in tool_results:
            messages.append({"role": "tool", "content": result["result"]})

        response = await ollama_client.chat(  # type: ignore
            model=ollama_config.model,
            messages=messages,
            stream=False,
        )

    return response["message"]["content"]
