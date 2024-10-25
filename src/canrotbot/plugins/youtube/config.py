from pydantic import BaseModel, Field


class YoutubeConfig(BaseModel):
    api_key: str = Field(default="", alias="youtube_api_key")
