from nonebot import get_driver, logger
from pathlib import Path
import sqlite3

_driver = get_driver()
_canrot_assets: dict[str, list[list]] = {}
_db = sqlite3.connect(Path(__file__).parent.parent.joinpath('assets.db').resolve())
_c = _db.cursor()

def load_all_assets():
    # get all table names
    table_names: set[str] = set()
    temp_c = _c.execute('select distinct tbl_name from sqlite_master')
    for i in temp_c.fetchall():
        table_names.add(i[0])
    logger.info(f'{len(table_names)} tables found')

    # get all data from tables
    for table_name in table_names:
        temp_c = _c.execute(f'select * from {table_name}')
        _canrot_assets[table_name] = temp_c.fetchall()
        logger.info(f'Load {len(_canrot_assets[table_name])} items from {table_name}')

if not _canrot_assets:
    load_all_assets()

def get_assets(table_name: str) -> list[list]:
    return _canrot_assets[table_name]

def execute_sql_on_assets(sql: str) -> list[list]:
    temp_c = _c.execute(sql)
    ret: list[list] = []
    col_name: list[str] = [t[0] for t in temp_c.description]
    ret.append(col_name)
    ret += temp_c.fetchall()
    return ret

@_driver.on_shutdown
async def _():
    _c.close()
    _db.close()
    logger.info('Closed database')
