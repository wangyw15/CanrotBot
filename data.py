from nonebot import get_driver, logger
from pydantic import BaseModel, validator
from typing import TypeVar, Any
import sqlite3

class AIOConfig(BaseModel):
    aio_enable: bool = True # always enable aio
    aio_data_path: str = './aio.db'
    aio_disable_plugins: list[str] = []

    @validator('aio_enable')
    def aio_enable_validator(cls, v):
        if not isinstance(v, bool):
            raise ValueError('aio_enable must be a bool')
        return v

    @validator('aio_data_path')
    def aio_data_path_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('aio_data_path must be a str')
        return v
    
    @validator('aio_disable_plugins')
    def aio_disable_plugins_validator(cls, v):
        if not isinstance(v, list):
            raise ValueError('aio_disable_plugins must be a list')
        for i in v:
            if not isinstance(i, str):
                raise ValueError('aio_disable_plugins must be a list of str')
        return v

__global_driver = get_driver().config
aio_config = AIOConfig.parse_obj(__global_driver)
__aio_all_data: dict[str, list[list]] = {}
aio_help_message: str = 'AIO插件帮助\n'

def load_all_data():
    db = sqlite3.connect(aio_config.aio_data_path)
    c = db.cursor()

    # get all table names
    table_names: set[str] = set()
    temp_c = c.execute('select distinct tbl_name from sqlite_master')
    for i in temp_c.fetchall():
        table_names.add(i[0])
    logger.info(f'{len(table_names)} tables found')

    # get all data from tables
    for table_name in table_names:
        temp_c = c.execute(f'select * from {table_name}')
        __aio_all_data[table_name] = temp_c.fetchall()
        logger.info(f'Load {len(__aio_all_data[table_name])} items from {table_name}')

if not __aio_all_data:
    load_all_data()

def get_data(table_name: str) -> list[list]:
    return __aio_all_data[table_name]

def get_config(name: str) -> Any:
    return __global_driver.dict()[name]

def add_help_message(command: str, description: str):
    global aio_help_message
    aio_help_message += f'/{command}: {description}\n'
