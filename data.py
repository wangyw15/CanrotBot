from nonebot import get_driver, logger
from pydantic import BaseModel, validator
from typing import TypeVar, Any
import sqlite3

class AIOConfig(BaseModel):
    aio_data_path: str = './aio.db'

    @validator('aio_data_path')
    def aio_data_path_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('aio_data_path must be a str')
        return v
    
__config = AIOConfig.parse_obj(get_driver().config)
__aio_all_data: dict[str, list[list]] = {}

def load_all_data():
    db = sqlite3.connect(__config.aio_data_path)
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
