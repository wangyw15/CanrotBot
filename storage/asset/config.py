from pydantic import BaseModel, Field


class AssetConfig(BaseModel):
    proxy: str = Field(default="")
