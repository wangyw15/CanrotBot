from nonebot import get_driver, logger
from pydantic import BaseModel, validator
from typing import Any

class CanrotConfig(BaseModel):
    canrot_enable: bool = True # always enable aio
    canrot_proxy: str = ''
    canrot_data: str = './canrot_data.db'

    @validator('canrot_enable')
    def canrot_enable_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('canrot_enable must be a bool')
        return v
    
    @validator('canrot_proxy')
    def canrot_proxy_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('canrot_proxy must be a str')
        if not v.startswith('https://') and not v.startswith('http://'):
            raise ValueError('canrot_proxy must start with https:// or http://')
        return v

    @validator('canrot_data')
    def canrot_data_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('canrot_data must be a str')
        return v

_driver = get_driver()
_global_config = _driver.config
canrot_config = CanrotConfig.parse_obj(_global_config)

def get_config(name: str) -> Any:
    return _global_config.dict()[name]
