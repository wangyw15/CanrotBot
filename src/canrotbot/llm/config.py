from nonebot import get_plugin_config
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    command_start: set[str] = Field(default={"/"})
    enabled: bool = Field(default=False, alias="canrot_llm_enabled")
    temperature: float = Field(default=0.3, alias="canrot_llm_temperature")
    max_length: int = Field(default=2**12, alias="canrot_llm_max_length")
    system_prompt: str = Field(
        default="You are an useful chat robot in an IM message group",
        alias="canrot_llm_system_prompt",
    )
    enable_tools: bool = Field(default=True, alias="canrot_llm_enable_tools")


llm_config = get_plugin_config(LLMConfig)
