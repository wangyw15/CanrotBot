import json

from nonebot import logger, on_message
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule, to_me
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Query,
    Subcommand,
    on_alconna,
)
from openai.types.chat import ChatCompletionUserMessageParam

from canrotbot.essentials.libraries import user
from canrotbot.libraries.llm import chat_completion, summarize_context

from . import context as context_manager
from . import wrapper as wrapper
from .config import LLMConfig, llm_plugin_config

__plugin_meta__ = PluginMetadata(
    name="LLM",
    description="提供大语言模型交互",
    usage="at机器人即可",
    config=LLMConfig,
)


async def not_command(event: Event) -> bool:
    for command_start in llm_plugin_config.command_start:
        if event.get_plaintext().startswith(command_start):
            return False
    return True


async def llm_enabled() -> bool:
    return llm_plugin_config.enabled


llm_matcher = on_message(
    priority=100, rule=Rule(not_command, llm_enabled) & to_me(), block=False
)


@llm_matcher.handle()
async def _(event: Event):
    # 获取会话上下文
    user_id = user.get_uid()
    messages: list[ChatCompletionUserMessageParam] = []
    if not user_id:
        await llm_matcher.send("当前为游客状态，对话无上下文")
    else:
        selected_context = context_manager.get_selected_context(user_id)
        if selected_context:
            messages = json.loads(selected_context.context)
            await llm_matcher.send(
                f"自动选择会话 {selected_context.id}"
                + (f". {selected_context.name}" if selected_context.name else "")
            )
        else:
            context_id = context_manager.create_context(user_id)
            await llm_matcher.send(f"没有已选的会话，自动创建新会话 {context_id}")
    messages.append({"role": "user", "content": event.get_plaintext()})

    answer = "后端无回复"
    try:
        new_messages, answer = await chat_completion(
            messages,
            with_tool_call=True,
            with_message_postprocessing=True,
            temperature=llm_plugin_config.temperature,
        )

        # 为新对话创建名称
        if user_id and len(messages) == 1:
            context_manager.update_selected_context(
                user_id, new_messages, name=await summarize_context(new_messages)
            )
    except Exception as e:
        logger.error("Error in llm plugin")
        logger.exception(e)
        await llm_matcher.finish(f"出现错误：\n{e}")

    if isinstance(answer, str):
        await llm_matcher.finish(answer)
    await llm_matcher.finish(await answer.export())


context_command = Alconna(
    "chat",
    Subcommand(
        "new",
        alias={"新建会话"},
    ),
    Subcommand(
        "list",
        alias={"会话列表"},
    ),
    Subcommand(
        "select",
        Args["select_context_id", int],
        alias={"选择会话"},
    ),
    Subcommand(
        "delete",
        Args["delete_context_id", int],
        alias={"删除会话"},
    ),
    # Subcommand(
    #     "copy",
    #     Args["copy_context_id", int],
    #     alias={"复制会话"},
    # ),
    meta=CommandMeta(description="管理LLM聊天上下文"),
)

context_matcher = on_alconna(
    context_command,
    block=True,
)


@context_matcher.handle()
async def _():
    if not user.get_uid():
        await context_matcher.finish("未注册用户无法使用")


@context_matcher.assign("new")
async def _():
    user_id = user.get_uid()
    context_id = context_manager.create_context(user_id)
    await llm_matcher.finish(f"已创建并选中新会话 {context_id}")


@context_matcher.assign("list")
async def _():
    user_id = user.get_uid()
    contexts = context_manager.get_all_context(user_id)
    if not contexts:
        await llm_matcher.finish("尚未创建过会话")

    message = "会话列表:\n"
    for i in contexts:
        message += (
            ("* " if i.selected else "")
            + f"{i.id}. "
            + (i.name if i.name else "空对话")
            + "\n"
        )
    await llm_matcher.finish(message.strip())


@context_matcher.assign("select")
async def _(context_id: Query[int] = Query("select_context_id")):
    user_id = user.get_uid()
    if context_manager.select_context(context_id.result, user_id):
        await llm_matcher.finish("选择成功")
    else:
        await llm_matcher.finish("选择失败，可能会话id不存在")


@context_matcher.assign("delete")
async def _(context_id: Query[int] = Query("delete_context_id")):
    user_id = user.get_uid()
    if context_manager.delete_context(context_id.result, user_id):
        await llm_matcher.finish("删除成功")
    else:
        await llm_matcher.finish("删除失败，可能会话id不存在")
