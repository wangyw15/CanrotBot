import ollama
from nonebot import get_plugin_config
from ollama import Message

from .config import OllamaConfig
from ... import tool

ollama_config = get_plugin_config(OllamaConfig)
ollama_client = ollama.AsyncClient(ollama_config.ollama_host)


async def chat(text: str) -> str:
    messages: list[Message] = [{"role": "user", "content": text}]

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
            tool_ret = tool.tools_callable[tool_name](**tool_args)
            messages.append({"role": "tool", "content": str(tool_ret)})

        response = await ollama_client.chat(
            model=ollama_config.ollama_model,
            messages=messages,
            stream=False,
        )

    return response["message"]["content"]
