from typing import Literal

from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    command_start: set[str] = Field(default={"/"})
    enabled: bool = Field(default=False, alias="canrot_llm_enabled")
    backend: Literal["ollama", "openai"] = Field(
        default="ollama", alias="canrot_llm_backend"
    )
