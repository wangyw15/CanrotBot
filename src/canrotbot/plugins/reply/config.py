from pydantic import BaseModel, Field

from .data import ReplyMode


class ReplyConfig(BaseModel):
    default_system_prompt: str = Field(
        default="", alias="canrot_reply_default_system_prompt"
    )
    default_rate: float = Field(default=0.1, alias="canrot_reply_default_rate")
    default_mode: ReplyMode = Field(
        default=ReplyMode.ARRISA, alias="canrot_reply_default_mode"
    )
