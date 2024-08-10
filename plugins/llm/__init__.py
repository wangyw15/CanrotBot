from nonebot import on_message, get_plugin_config
from nonebot.adapters import Event
from nonebot.rule import Rule, to_me
from nonebot_plugin_alconna import UniMessage

from libraries.llm.llm_backend import ollama_chat, openai_chat
from .config import LLMConfig

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
    extra = UniMessage()
    if config.backend == "ollama":
        answer, extra = await ollama_chat(event.get_plaintext())
    elif config.backend == "openai":
        answer, extra = await openai_chat(event.get_plaintext())
    await llm.finish(await (UniMessage.text(answer) + extra).export())
