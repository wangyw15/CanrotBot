from nonebot import on_message, get_plugin_config
from nonebot.adapters import Event
from nonebot.rule import Rule

from .config import LLMConfig
from .llm_backend import ollama_backend

config = get_plugin_config(LLMConfig)


async def not_command(event: Event) -> bool:
    for command_start in config.command_start:
        if event.get_plaintext().startswith(command_start):
            return False
    return True


async def llm_enabled() -> bool:
    return config.enabled


llm = on_message(priority=100, rule=Rule(not_command, llm_enabled), block=False)


@llm.handle()
async def _(event: Event):
    answer = await ollama_backend.chat(event.get_plaintext())
    await llm.finish(answer)
