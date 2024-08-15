from nonebot import on_message, get_plugin_config, logger
from nonebot.adapters import Event
from nonebot.rule import Rule, to_me

from libraries.llm.llm_backend import ollama_chat, openai_chat
from .config import LLMConfig
from .wrapper import *

config = get_plugin_config(LLMConfig)


async def not_command(event: Event) -> bool:
    for command_start in config.command_start:
        if event.get_plaintext().startswith(command_start):
            return False
    return True


async def llm_enabled() -> bool:
    return config.enabled


llm = on_message(
    priority=100, rule=Rule(not_command, llm_enabled) & to_me(), block=False
)


@llm.handle()
async def _(event: Event):
    answer = "后端无回复"

    try:
        if config.backend == "ollama":
            chat = ollama_chat
        elif config.backend == "openai":
            chat = openai_chat
        else:
            raise NotImplementedError(f"Invalid backend: {config.backend}")
        answer = await chat(
            event.get_plaintext(),
            with_tool_call=True,
            with_message_postprocessing=True,
            temperature=config.tempurature,
        )
    except Exception as e:
        logger.error("Error in llm plugin")
        logger.exception(e)
        await llm.finish(f"出现错误：\n{e}")

    if isinstance(answer, str):
        await llm.finish(answer)
    await llm.finish(await answer.export())
