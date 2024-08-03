from pydantic import BaseModel


class TencentCloudConfig(BaseModel):
    secret_id: str = ""
    secret_key: str = ""
