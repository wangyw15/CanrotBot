from pydantic import BaseModel, Field


class NetworkConfig(BaseModel):
    proxy: str = Field(default="")  # 代理连接
    timeout: float = Field(default=10.0, alias="canrot_http_timeout")  # HTTP超时时间
