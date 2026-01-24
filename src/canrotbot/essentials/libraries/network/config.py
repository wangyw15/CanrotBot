from pydantic import BaseModel, Field


class NetworkConfig(BaseModel):
    proxy: str = Field(default="")  # 代理连接
