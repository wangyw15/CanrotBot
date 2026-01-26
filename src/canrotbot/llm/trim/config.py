from typing import Literal

from langchain.agents.middleware.summarization import ContextSize
from pydantic import BaseModel, Field


class TrimConfig(BaseModel):
    method: Literal["none", "trim", "summarize"] = Field(
        default="none", alias="canrot_llm_trim_method"
    )
    trim_keep: int = Field(default=20, alias="canrot_llm_trim_keep")

    summarize_trigger: ContextSize | list[ContextSize] | None = Field(
        default=("tokens", 4000), alias="canrot_llm_trim_summarize_trigger"
    )
    summarize_keep: ContextSize = Field(
        default=("messages", 20), alias="canrot_llm_trim_summarize_trigger"
    )
