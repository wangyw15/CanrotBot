from nonebot import get_driver, logger, load_plugin
from nonebot.plugin import Plugin
from pydantic import BaseModel, validator
from typing import Any
from pathlib import Path
import sqlite3
import os

class AIOConfig(BaseModel):
    aio_enable: bool = True # always enable aio
    aio_proxy: str = ''
    aio_disable_plugins: list[str] = []

    @validator('aio_enable')
    def aio_enable_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('aio_enable must be a bool')
        return v
    
    @validator('aio_proxy')
    def aio_proxy_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('aio_proxy must be a str')
        if not v.startswith('https://') and not v.startswith('http://'):
            raise ValueError('aio_proxy must start with https:// or http://')
        return v

    @validator('aio_disable_plugins')
    def aio_disable_plugins_validator(cls, v):
        if not isinstance(v, list):
            raise ValueError('aio_disable_plugins must be a list')
        for i in v:
            if not isinstance(i, str):
                raise ValueError('aio_disable_plugins must be a list of str')
        return v

__driver = get_driver()
__global_config = __driver.config
aio_config = AIOConfig.parse_obj(__global_config)
__aio_all_data: dict[str, list[list]] = {}
__db = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'assets.db'))
__c = __db.cursor()
loaded_plugins: list[Plugin] = []

def load_plugins() -> None:
    plugins_path = Path(__file__).parent.joinpath('plugins').resolve()
    for p in plugins_path.glob('*.py'):
        if p.name[:-3] not in aio_config.aio_disable_plugins:
            loaded_plugins.append(load_plugin(p.resolve()))

def load_all_data():
    # get all table names
    table_names: set[str] = set()
    temp_c = __c.execute('select distinct tbl_name from sqlite_master')
    for i in temp_c.fetchall():
        table_names.add(i[0])
    logger.info(f'{len(table_names)} tables found')

    # get all data from tables
    for table_name in table_names:
        temp_c = __c.execute(f'select * from {table_name}')
        __aio_all_data[table_name] = temp_c.fetchall()
        logger.info(f'Load {len(__aio_all_data[table_name])} items from {table_name}')

if not __aio_all_data:
    load_all_data()

def get_data(table_name: str) -> list[list]:
    return __aio_all_data[table_name]

def get_config(name: str) -> Any:
    return __global_config.dict()[name]

def execute_sql(sql: str) -> list[list]:
    temp_c = __c.execute(sql)
    ret: list[list] = []
    col_name: list[str] = [t[0] for t in temp_c.description]
    ret.append(col_name)
    ret += temp_c.fetchall()
    return ret

@__driver.on_shutdown
async def _():
    __c.close()
    __db.close()
    logger.info('Closed database')
