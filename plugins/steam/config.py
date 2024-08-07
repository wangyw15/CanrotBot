from pydantic import BaseModel, Field


class SteamConfig(BaseModel):
    region: str = Field(default="cn", alias="steam_region")
    language: str = Field(default="zh-cn", alias="steam_language")
