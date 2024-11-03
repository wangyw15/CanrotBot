from pydantic import BaseModel, Field


class NetworkConfig(BaseModel):
    proxy: str = Field(default="")  # 代理连接
    cache_ttl: int = Field(default=0, alias="canrot_cache_ttl")  # 缓存有效时间
    timeout: float = Field(default=10.0, alias="canrot_http_timeout")  # 缓存有效时间
