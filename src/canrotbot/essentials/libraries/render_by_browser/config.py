from pydantic import BaseModel, Field


class RenderByBrowserConfig(BaseModel):
    proxy: str = Field(default="")
