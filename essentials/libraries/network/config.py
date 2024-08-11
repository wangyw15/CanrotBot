from pydantic import BaseModel, Field


class NetworkConfig(BaseModel):
    proxy: str = Field(default="")  # 代理连接
    cache_ttl: int = Field(default=0)  # 缓存有效时间
