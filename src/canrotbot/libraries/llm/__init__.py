from typing import cast

from nonebot import get_plugin_config
from nonebot_plugin_alconna import UniMessage
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import ChatCompletion, Choice

from . import tool
from .config import OpenAIConfig
from .tool.model import ToolCallResult

openai_config = get_plugin_config(OpenAIConfig)
openai_client = AsyncOpenAI(
    base_url=openai_config.base_url, api_key=openai_config.api_key
)


async def chat_completion(
    message: list[ChatCompletionMessageParam] | str,
    with_tool_call: bool = True,
    with_message_postprocessing: bool = False,
    **kwargs,
) -> tuple[list[ChatCompletionMessageParam], str | UniMessage]:
    """
    生成聊天回复

    :param message: 消息
    :param with_tool_call: 是否使用 tool_call
    :param with_message_postprocessing: 是否使用消息后处理，仅在 with_tool_call 为 True 时有效
    :param kwargs: OpenAIClient 的参数

    :return: 返回消息：str 则为普通消息，UniMessage 则为经过后处理消息
    """
    if isinstance(message, str):
        messages: list[ChatCompletionMessageParam] = [
            {"role": "user", "content": message}
        ]
    else:
        messages: list[ChatCompletionMessageParam] = cast(
            list[ChatCompletionMessageParam], [i.copy() for i in message]
        )

    finish_reason: str | None = None
    choice: None | Choice = None
    all_tool_results: list[ToolCallResult] = []

    while finish_reason is None or finish_reason != "stop":
        completion: ChatCompletion = await openai_client.chat.completions.create(  # type: ignore
            model=openai_config.model,
            messages=messages,
            stream=False,
            tools=tool.tools_description if openai_config.enable_tools and with_tool_call else None,
            **kwargs,
        )

        choice = completion.choices[0]
        messages.append(choice.message.model_dump(exclude={"reasoning_content"}))
        finish_reason = choice.finish_reason

        if finish_reason == "tool_calls":
            tool_calls = completion.choices[0].message.tool_calls or []

            tool_results = await tool.run_tool_call(tool_calls)
            for result in tool_results:
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": result.tool_call_id,
                        "name": result.name,
                        "content": result.result,
                    }
                )
            all_tool_results.extend(tool_results)

    if not choice or not choice.message.content:
        return messages, ""

    final_message: str = choice.message.content

    if with_tool_call and with_message_postprocessing:
        return messages, await tool.run_message_postprocess(
            final_message, all_tool_results
        )
    else:
        return messages, final_message


async def summarize_context(context: list[ChatCompletionMessageParam] | str) -> str:
    """
    概括上下文对话内容

    :param context: 上下文内容

    :return: 对话摘要内容
    """
    new_context = context.copy()
    new_context.append(
        {
            "role": "user",
            "content": "Summarize the subject of the conversation in a descriptive format with no more than 10 words in the above language",
        }
    )
    new_context, result = await chat_completion(
        new_context, with_tool_call=False, with_message_postprocessing=False
    )
    return new_context[-1]["content"]
