from pydantic import BaseModel, Field


class TencentCloudConfig(BaseModel):
    secret_id: str = Field(default="", alias="tencent_cloud_secret_id")
    secret_key: str = Field(default="", alias="tencent_cloud_secret_key")
