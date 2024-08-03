from pydantic import BaseModel


class NetworkConfig(BaseModel):
    proxy: str = ""  # 代理连接
