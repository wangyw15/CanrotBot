import json
import typing
from pathlib import Path

from .config import canrot_config

_base_data_dir = Path(canrot_config.canrot_data_dir)
_dict_data: dict[str, dict[str, str]] = {}
_file_pointers: dict[Path, typing.IO] = {}
_DICT_FILE_NAME = '_dict.json'
_DEFAULT_DICT_NAME = '_default'


def _get_file_pointer(path: Path) -> typing.IO:
    if path not in _file_pointers:
        _file_pointers[path] = path.open(encoding='utf-8')
    return _file_pointers[path]


# 创建数据目录
_base_data_dir.mkdir(parents=True, exist_ok=True)
# 加载数据
if (_base_data_dir / _DICT_FILE_NAME).exists():
    _dict_data['_default'] = json.load(_get_file_pointer(_base_data_dir / _DICT_FILE_NAME))
else:
    _dict_data['_default'] = {}
for i in _base_data_dir.iterdir():
    if i.is_dir() and (i / _DICT_FILE_NAME).exists():
        _dict_data[i.name] = json.load(_get_file_pointer(i / _DICT_FILE_NAME))


def get_base_dir() -> Path:
    return _base_data_dir


def get_data_dir(name: str) -> Path:
    return _base_data_dir / name


def get_value(key: str, name: str = '') -> str:
    if not name:
        name = _DEFAULT_DICT_NAME
    return _dict_data[name][key]


def set_value(key: str, value: str,  name: str = '') -> None:
    if name:
        _dict_data[name][key] = value
    else:
        _dict_data[_DEFAULT_DICT_NAME][key] = value
    fp = _get_file_pointer(_base_data_dir / name / _DICT_FILE_NAME)
    fp.seek(0)
    json.dump(_dict_data[name], fp, ensure_ascii=False)
    fp.flush()
