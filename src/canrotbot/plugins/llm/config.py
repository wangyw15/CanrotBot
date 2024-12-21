from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    command_start: set[str] = Field(default={"/"})
    enabled: bool = Field(default=False, alias="canrot_llm_enabled")
    temperature: float = Field(default=0.3, alias="canrot_llm_temperature")
    max_length: int = Field(default=2**12, alias="canrot_llm_max_length")


llm_plugin_config = get_plugin_config(LLMConfig)
