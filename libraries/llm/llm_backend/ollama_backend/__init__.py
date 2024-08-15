import ollama
from nonebot import get_plugin_config
from nonebot_plugin_alconna import UniMessage

from .config import OllamaConfig
from ... import tool
from ...model import Message
from ...tool.model import ToolCallResult

ollama_config = get_plugin_config(OllamaConfig)
ollama_client = ollama.AsyncClient(ollama_config.host)


async def chat(
    message: list[Message] | str,
    with_tool_call: bool = True,
    with_message_postprocessing: bool = False,
) -> str | UniMessage:
    """
    生成聊天回复

    :param message: 消息
    :param with_tool_call: 是否使用 tool_call
    :param with_message_postprocessing: 是否使用消息后处理，仅在 with_tool_call 为 True 时有效

    :return: 返回消息：str 则为普通消息，UniMessage 则为经过后处理消息
    """
    if isinstance(message, str):
        messages: list[Message] = [{"role": "user", "content": message}]
    else:
        messages = [i.copy() for i in message]

    response = await ollama_client.chat(  # type: ignore
        model=ollama_config.model,
        messages=messages,
        stream=False,
        tools=tool.tools_description if with_tool_call else None,
    )
    tool_results: list[ToolCallResult] = []

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

    final_message: str = response["message"]["content"]

    if with_tool_call and with_message_postprocessing:
        return tool.run_message_postprocess(final_message, tool_results)
    else:
        return final_message
