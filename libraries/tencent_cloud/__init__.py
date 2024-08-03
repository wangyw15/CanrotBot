from tencentcloud.common import credential
from nonebot import get_plugin_config
from .config import TencentCloudConfig

config = get_plugin_config(TencentCloudConfig)


def create_credential() -> credential.Credential:
    if not all([config.secret_id, config.secret_key]):
        raise ValueError("腾讯云 API 密钥未配置")
    return credential.Credential(config.secret_id, config.secret_key)
