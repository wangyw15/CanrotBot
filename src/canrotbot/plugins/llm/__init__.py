from nonebot import logger, on_message
from nonebot.adapters import Event
from nonebot.rule import Rule, to_me

from canrotbot.libraries.llm.llm_backend import ollama_chat, openai_chat

from . import wrapper as wrapper
from .config import llm_plugin_config


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
    answer = "后端无回复"

    try:
        if llm_plugin_config.backend == "ollama":
            chat = ollama_chat
        elif llm_plugin_config.backend == "openai":
            chat = openai_chat
        else:
            raise NotImplementedError(f"Invalid backend: {llm_plugin_config.backend}")
        answer = await chat(
            event.get_plaintext(),
            with_tool_call=True,
            with_message_postprocessing=True,
            temperature=llm_plugin_config.tempurature,
        )
    except Exception as e:
        logger.error("Error in llm plugin")
        logger.exception(e)
        await llm_matcher.finish(f"出现错误：\n{e}")

    if isinstance(answer, str):
        await llm_matcher.finish(answer)
    await llm_matcher.finish(await answer.export())
