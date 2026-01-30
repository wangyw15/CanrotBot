from datetime import datetime

from langchain.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    ToolCall,
)
from langchain_core.load import loads
from nonebot import logger, on_message
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import (
    MessageEvent as ob11MessageEvent,
)
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule, to_me
from nonebot.typing import T_State
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    MsgTarget,
    Query,
    Subcommand,
    UniMsg,
    on_alconna,
)

from canrotbot.essentials.libraries import user

from ..chat import get_agent, summarize_context
from ..chat.model import ChatContext
from ..config import LLMConfig, llm_config
from . import context as context_manager
from . import utils as utils

__plugin_meta__ = PluginMetadata(
    name="LLM",
    description="提供大语言模型交互",
    usage="at机器人即可",
    config=LLMConfig,
)


async def not_command(event: Event) -> bool:
    for command_start in llm_config.command_start:
        if event.get_plaintext().startswith(command_start):
            return False
    return True


async def llm_enabled() -> bool:
    return llm_config.enabled


llm_matcher = on_message(
    priority=100, rule=Rule(not_command, llm_enabled) & to_me(), block=False
)


@llm_matcher.handle()
async def _(
    event: ob11MessageEvent,
    state: T_State,
):
    # 获取用户昵称
    state["nickname"] = event.sender.nickname

    # 获取回复内容
    if event.reply is not None:
        state["quote"] = event.reply.message.extract_plain_text()


@llm_matcher.handle()
async def _(
    event: Event,
    target: MsgTarget,
    state: T_State,
    msg: UniMsg,
):
    agent = await get_agent()
    user_id = user.get_uid()

    # 获取会话上下文
    context_name: str = ""
    messages: list[AnyMessage] = []
    if not user_id:
        await llm_matcher.send("当前为游客状态，对话不保存历史记录")
    else:
        selected_context = context_manager.get_selected_context(user_id)
        if selected_context:
            context_name = selected_context.name
            messages = loads(selected_context.context)
            await llm_matcher.send(
                f"自动选择会话 {selected_context.id}"
                + (f". {selected_context.name}" if selected_context.name else "")
            )
        else:
            context_id = context_manager.create_context(user_id)
            await llm_matcher.send(f"没有已选的会话，自动创建新会话 {context_id}")

    messages.append(HumanMessage(msg.extract_plain_text()))
    new_conversation = len(messages) == 1

    # context engineering
    context = ChatContext(
        private_chat=target.private,
        channel_chat=target.channel,
        self_id=target.self_id,
        platform_id=target.id,
        user_id=user_id,
        name=state.get("nickname", ""),
        time=datetime.now(),
        quote=state.get("quote", ""),
        markdown=False,
    )

    answer: str = "后端无回复"
    try:
        response = await agent.ainvoke(
            {
                "messages": messages,
            },  # type: ignore
            context=context,
        )
        messages = response["messages"]
        answer = messages[-1].content

        # 输出调用的tools
        called_tools: list[ToolCall] = []
        for i in range(len(messages) - 2, -1, -1):
            current_msg = messages[i]

            if current_msg.type == "ai" and isinstance(current_msg, AIMessage):
                for j in range(len(current_msg.tool_calls) - 1, -1, -1):
                    called_tools.append(current_msg.tool_calls[j])
            if current_msg.type == "human":
                break

        called_tools.reverse()
        for i in called_tools:
            logger.debug(f"Called tool {i['name']} with {i['args']}")

        # 更新上下文
        if user_id:
            # 为新对话创建名称
            if new_conversation:
                context_name = await summarize_context(messages)

            context_manager.update_selected_context(
                user_id, messages, name=context_name
            )
    except Exception as e:
        logger.error("Error in llm plugin")
        logger.exception(e)
        await llm_matcher.finish(f"出现错误：\n{e}")

    await llm_matcher.finish(answer)


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
