from pydantic import BaseModel, Field


class BangDreamConfig(BaseModel):
    default_language: str = Field(default="cn", alias="bang_dream_language")
