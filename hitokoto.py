from nonebot import get_driver, on_command
from nonebot.plugin import PluginMetadata

from pydantic import BaseModel, validator
import requests

# config
class HitokotoConfig(BaseModel):
    hitokoto_enabled: bool = True

    @validator('hitokoto_enabled')
    def hitokoto_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('hitokoto_enabled must be a bool')
        return v

config = HitokotoConfig.parse_obj(get_driver().config)

# metadata
__plugin_meta__ = PluginMetadata(
    name='Hitokoto',
    description='Hitokoto Plugin',
    usage='/hitokoto',
    config=HitokotoConfig,
    extra={}
)

async def is_enabled() -> bool:
    return config.hitokoto_enabled

# message
hitokoto = on_command('hitokoto', aliases={'一言'}, rule=is_enabled, block=True)

def fetch_hitokoto():
    """Fetch Hitokoto"""
    r = requests.get('https://v1.hitokoto.cn/?c=a&c=b&c=c')
    data = r.json()
    return f'{data["hitokoto"]}\n-- {"" if not data["from_who"] else data["from_who"]}「{data["from"]}」\nhttps://hitokoto.cn/?uuid={data["uuid"]}'

@hitokoto.handle()
async def hitokoto_handle():
    """Hitokoto Handler"""
    await hitokoto.finish(fetch_hitokoto())
