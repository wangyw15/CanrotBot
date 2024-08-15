from typing import Literal

from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    command_start: set[str] = Field(default={"/"})
    enabled: bool = Field(default=False, alias="canrot_llm_enabled")
    tempurature: float = Field(default=0.3, alias="canrot_llm_tempurature")
    max_length: int = Field(default=2**12, alias="canrot_llm_max_length")
    backend: Literal["ollama", "openai"] = Field(
        default="ollama", alias="canrot_llm_backend"
    )


llm_plugin_config = get_plugin_config(LLMConfig)
